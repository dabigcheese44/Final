document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('login-form');
    const errorBox = document.getElementById('error-message');
    const counter = document.getElementById('attempt-count');
  
    let attempts = 0;
  
    form.addEventListener('submit', (e) => {
      e.preventDefault();
  
      const email = document.getElementById('email').value.trim();
      const password = document.getElementById('password').value;
  
      jQuery.ajax({
        url: '/processsignup',
        method: 'POST',
        data: { email, password },
        success: (res) => {
          const result = JSON.parse(res);
  
          if (result.success) {
            window.location.href = result.redirect;
          } else {
            attempts++;
            showError(result.message);
          }
        },
        error: () => {
          showError('Something went wrong. Please try again.');
        }
      });
    });
  
    function showError(msg) {
      errorBox.textContent = msg;
      errorBox.style.display = 'block';
  
      counter.textContent = attempts;
      counter.style.display = 'block';
    }
  });
  