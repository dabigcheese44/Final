document.addEventListener('DOMContentLoaded', () => {
    const form           = document.getElementById('create-event-form');
    const addEmailButton = document.getElementById('add-email');
    const container      = document.getElementById('emails-container');
  
    /** Add one email input row */
    function addEmailRow(value = '') {
      const row   = document.createElement('div');
      row.className = 'email-entry';
  
      const input = document.createElement('input');
      input.type  = 'email';
      input.required = true;
      input.placeholder = 'name@example.com';
      input.value = value;
  
      const remove = document.createElement('button');
      remove.type = 'button';
      remove.className = 'remove-email-btn';
      remove.textContent = 'Remove';
      remove.onclick = () => row.remove();
  
      row.appendChild(input);
      row.appendChild(remove);
      container.appendChild(row);
    }
  
    addEmailRow();                       // default first row
    addEmailButton.onclick = () => addEmailRow();
  
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
  
      const fd = new FormData(form);
      container.querySelectorAll('input[type="email"]').forEach(inp => {
        const val = inp.value.trim();
        if (val) fd.append('invitees[]', val);
      });
  
      try {
        const res  = await fetch('/processevent', { method: 'POST', body: fd });
        const data = await res.json();
        if (data.success) {
          window.location.href = data.redirect;
        } else {
          alert(data.message || 'Error creating event');
        }
      } catch (err) {
        console.error(err);
        alert('Network error while creating event.');
      }
    });
  });
  