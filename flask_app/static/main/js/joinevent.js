document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.event-item').forEach(item => {
      item.addEventListener('click', () => {
        const id = item.dataset.id;
        if (id) window.location.href = `/event?event_id=${id}`;
      });
    });
  });
  