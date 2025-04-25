document.addEventListener('DOMContentLoaded', () => {
    /* ----------------------- globals ----------------------- */
    const tableBody   = buildGrid();          // returns <tbody>
    const modeSelect  = document.getElementById('mode');
    let   currentMode = modeSelect.value;
    modeSelect.onchange = () => currentMode = modeSelect.value;
  
    /* ------------------- load saved data ------------------ */
    fetch('/geteventdata')
      .then(r=>r.json())
      .then(data=>{
        if (data.success) {
          applyAvailability(data.avail);
          recalcHeatmap();
          recalcBestTime();
        }
      });
  
    /* ------------------ click-drag logic ------------------ */
    let isDown=false, anchor=null, changedCells=new Set();
  
    tableBody.addEventListener('mousedown', e=>{
      const cell = goodCell(e.target); if(!cell) return;
      isDown=true; anchor=cell;
      paint(cell); changedCells.add(cell);
      e.preventDefault();
    });
    tableBody.addEventListener('mouseover', e=>{
      if(!isDown) return;
      const cell = goodCell(e.target); if(!cell) return;
      paintRect(anchor, cell);
    });
    window.addEventListener('mouseup', ()=>{
      if(!isDown) return;
      isDown=false;
      if(changedCells.size) saveChanges(Array.from(changedCells));
      changedCells.clear();
    });
  
    /* ---------------- socket live update ------------------ */
    const socket = io('/event');
    window.socket = socket; 
    socket.on('availability_updated', data => {
        applyAvailability(data.avail);   // repaint personal layer
        recalcHeatmap();                 // redraw group intensity
        recalcBestTime();                // update banner
    });
    
    /* join room – payload not required, handler ignores arg */
    socket.emit('join_event', {});                      // let server place us in room
    socket.on('availability_updated', data=>{
      applyAvailability(data.avail);
      recalcHeatmap();
      recalcBestTime();
    });
  
    /* ================ helper functions ==================== */
    function goodCell(el){
      const td = el.closest('td');
      return td && !td.classList.contains('time-col') ? td : null;
    }
  
    function paint(td){
      td.classList.remove('available','maybe','unavailable');
      td.classList.add(currentMode);
      changedCells.add(td);
    }
  
    function paintRect(a,b){
      const [r1,c1]=idx(a), [r2,c2]=idx(b);
      const [rMin,rMax]=[Math.min(r1,r2),Math.max(r1,r2)];
      const [cMin,cMax]=[Math.min(c1,c2),Math.max(c1,c2)];
      tableBody.querySelectorAll('tr').forEach((tr,r)=>{
        if(r<rMin||r>rMax) return;
        Array.from(tr.children).forEach((td,c)=>{
          if(td.classList.contains('time-col')) return;
          if(c<cMin||c>cMax) return;
          paint(td);
        });
      });
    }
  
    function idx(td){
      const tr=td.parentElement;
      return [
        Array.from(tr.parentElement.children).indexOf(tr),
        Array.from(tr.children).indexOf(td)
      ];
    }
  
    /* ---------- save to server (batch) ---------- */
    function saveChanges(cells){
      const rows = cells.map(td=>[
        EVENT_META.event_id,
        EVENT_META.current_user,
        td.dataset.date + ' ' + td.dataset.time,
        td.classList.contains('available') ? 'available'
          : td.classList.contains('maybe') ? 'maybe' : 'unavailable'
      ]);
      fetch('/setavailability',{
        method:'POST',
        headers:{'Content-Type':'application/json'},
        body:JSON.stringify({rows})
      }).then(r=>r.json()).then(console.log);
      recalcHeatmap();
      recalcBestTime();
    }
  
    /* ---------- apply server data to grid ---------- */
    function applyAvailability(rows){
      // reset personal classes then reapply
      tableBody.querySelectorAll('td').forEach(td=>{
        td.classList.remove('available','maybe','unavailable');
      });
      rows.forEach(r=>{
        const [user,slot,status]=[r.user_id, r.slot_start, r.avail_status];
        // only mark our own personal layer (others show via heatmap)
        if(user!==EVENT_META.current_user) return;
        const [d,t]=slot.split(' ');
        const td = tableBody.querySelector(`td[data-date="${d}"][data-time="${t}"]`);
        if(td) td.classList.add(status);
      });
    }
  
    /* ---------- heat-map counts / classes ---------- */
    function recalcHeatmap() {
        /* 1. clear all previous group classes */
        tableBody.querySelectorAll('td').forEach(td =>
        td.classList.remove('g-1','g-2','g-3','m','u')
        );
    
        /* 2. fetch latest aggregate availability */
        fetch('/geteventdata')
        .then(r => r.json())
        .then(data => {
            if (!data.success) return;
    
            /* slot → { a: #available, m: #maybe, u: #unavailable } */
            const slots = {};
            data.avail.forEach(({ slot_start, avail_status }) => {
            const s = slots[slot_start] || (slots[slot_start] = { a:0, m:0, u:0 });
            if      (avail_status === 'available')   s.a += 1;
            else if (avail_status === 'maybe')       s.m += 1;
            else if (avail_status === 'unavailable') s.u += 1;
            });
    
            /* 3. apply colour classes per rules */
            Object.entries(slots).forEach(([slot, c]) => {
            const [d, t] = slot.split(' ');
            const td = tableBody.querySelector(
                `td[data-date="${d}"][data-time="${t}"]`
            );
            if (!td) return;
    
            if (c.a > 0) {                // at least one Available
                td.classList.add(
                c.a >= 3 ? 'g-3' :                // 3+ avail
                c.a === 2 ? 'g-2' : 'g-1'         // 2 or 1 avail
                );
            } else if (c.m > 0) {          // no Avail, some Maybe
                td.classList.add('m');
            } else {                       // only Unavailable
                td.classList.add('u');
            }
            });
        });
    }
  
    /* ---------- Best-Time banner ---------- */
    function recalcBestTime(){
      fetch('/geteventdata')
        .then(r=>r.json())
        .then(data=>{
          if(!data.success) return;
          const slots={};
          data.avail.forEach(r=>{
            const slot=r.slot_start;
            slots[slot]=slots[slot]||{a:0,u:0};
            if(r.avail_status==='available')   slots[slot].a++;
            else if(r.avail_status==='unavailable') slots[slot].u++;
          });
          // choose best slot
          const best = Object.entries(slots).sort(([,x],[,y])=>{
            if(y.a!==x.a) return y.a-x.a;
            if(x.u!==y.u) return x.u-y.u;
            return x.slot<y.slot?-1:1;
          })[0];
          const banner = document.getElementById('best-time');
          const span   = document.getElementById('best-time-slot');
          if(!best){
            banner.classList.add('hidden');
          }else{
            const slot=best[0];
            const [d,t]=slot.split(' ');
            span.textContent = `${d} @ ${t.slice(0,5)}`;
            banner.classList.remove('hidden');
          }
        });
    }
  
    /* ---------- grid builder (same as before) -------- */
    function buildGrid(){
      const wrapper=document.getElementById('grid-wrapper');
      const tbl=document.createElement('table');tbl.className='grid-table';
      const thead=document.createElement('thead');const hr=document.createElement('tr');
      hr.appendChild(document.createElement('th'));
      dateRange(EVENT_META.start_date, EVENT_META.end_date).forEach(d=>{
        const th=document.createElement('th');
        th.textContent=d.toLocaleDateString(undefined,{weekday:'short',month:'numeric',day:'numeric'});
        hr.appendChild(th);});
      thead.appendChild(hr);tbl.appendChild(thead);
      const tbody=document.createElement('tbody');
      const [s,e]=[EVENT_META.day_start,EVENT_META.day_end].map(toMin);
      for(let t=s;t<e;t+=30){
        const tr=document.createElement('tr');
        const lab=document.createElement('td');lab.className='time-col';lab.textContent=minLbl(t);
        tr.appendChild(lab);
        dateRange(EVENT_META.start_date,EVENT_META.end_date).forEach(d=>{
          const td=document.createElement('td');
          td.dataset.date=d.toISOString().slice(0,10);
          td.dataset.time=minLbl(t,true);
          tr.appendChild(td);});
        tbody.appendChild(tr);}
      tbl.appendChild(tbody);wrapper.appendChild(tbl);
      return tbody;
    }
    function dateRange(s,e){const a=[];let d=new Date(s);const E=new Date(e);
      while(d<=E){a.push(new Date(d));d.setDate(d.getDate()+1);}return a;}
    function toMin(hms){const[h,m]=hms.split(':');return +h*60+ +m;}
    function minLbl(m,sec=false){
      const h=String(Math.floor(m/60)).padStart(2,'0');
      const mm=String(m%60).padStart(2,'0');
      return sec?`${h}:${mm}:00`:`${h}:${mm}`;}
  });
  