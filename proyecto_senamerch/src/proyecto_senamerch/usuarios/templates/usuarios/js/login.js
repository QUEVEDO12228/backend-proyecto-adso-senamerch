document.addEventListener('DOMContentLoaded', () => {
  const toggleBtn = document.querySelector('.login__toggle-password');
  const passwordInput = document.getElementById('password');

  if (!toggleBtn || !passwordInput) return;

  toggleBtn.addEventListener('click', () => {
    const isPassword = passwordInput.type === 'password';

    passwordInput.type = isPassword ? 'text' : 'password';
    toggleBtn.textContent = isPassword ? 'Ocultar' : 'Mostrar';
  });
});
