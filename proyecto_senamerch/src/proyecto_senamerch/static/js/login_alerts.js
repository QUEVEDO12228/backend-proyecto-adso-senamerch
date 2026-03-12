console.log('JS de login cargado');

document.addEventListener('DOMContentLoaded', () => {

  // ===============================
  // ALERTAS DE DJANGO
  // ===============================
  const alerts = document.querySelectorAll('.alert');
  alerts.forEach((alert) => {
    // Mostrar alerta con animación
    setTimeout(() => {
      alert.classList.add('show');
    }, 200);

    // Ocultar automáticamente después de 4 segundos
    setTimeout(() => {
      alert.classList.remove('show');
      setTimeout(() => alert.remove(), 500);
    }, 4000);
  });

  // ===============================
  // MOSTRAR / OCULTAR CONTRASEÑA
  // ===============================
  const toggleBtn = document.querySelector('.login__toggle-password');
  const passwordInput = document.getElementById('password');

  if (toggleBtn && passwordInput) {
    toggleBtn.addEventListener('click', () => {
      const isPassword = passwordInput.type === 'password';
      passwordInput.type = isPassword ? 'text' : 'password';
      toggleBtn.textContent = isPassword ? 'Ocultar' : 'Mostrar';
    });
  }

  // ===============================
  // VALIDACIÓN FRONTEND (opcional)
  // ===============================
  const form = document.getElementById('loginForm');
  const emailInput = document.getElementById('email');
  const passwordInput2 = document.getElementById('password');
  const emailError = document.getElementById('emailError');
  const passwordError = document.getElementById('passwordError');

  if (form) {
    form.addEventListener('submit', function (e) {
      let valid = true;
      const email = emailInput.value.trim();
      const password = passwordInput2.value.trim();

      // Validación EMAIL
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!emailRegex.test(email)) {
        emailError.textContent = 'Correo inválido';
        valid = false;
      } else {
        emailError.textContent = '';
      }

      // Validación PASSWORD
      if (password.length < 3) {
        passwordError.textContent = 'Mínimo 6 caracteres';
        valid = false;
      } else {
        passwordError.textContent = '';
      }

      if (!valid) e.preventDefault();
    });
  }

  // ===============================
  // REDIRECCIÓN POST LOGIN EXITOSO
  // ===============================
  // Redirección después de mostrar alerta de éxito
    if (form && form.dataset.redirectUrl) {
    setTimeout(() => {
        window.location.href = form.dataset.redirectUrl;
    }, 2000); // espera 2 segundos para que veas la alerta
    }

});