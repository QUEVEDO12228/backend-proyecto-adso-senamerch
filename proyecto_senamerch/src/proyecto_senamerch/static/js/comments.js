// static/js/comments.js  (ES module)

export function initCommentsSidebar() {
  initMenuToggle();
  initSidebar();
}

/* ===============================
   MENÚ DE LOS 3 PUNTOS (⋮)
================================ */
function initMenuToggle() {
  document.addEventListener("click", (e) => {
    const btn = e.target.closest(".product-card__menu-btn");
    const anyMenu = document.querySelectorAll(".product-card__menu-dropdown");

    // cerrar todos si se hace click fuera
    if (!btn) {
      anyMenu.forEach(m => m.classList.remove("product-card__menu-dropdown--active"));
      return;
    }

    e.preventDefault();

    const menu = btn.nextElementSibling;
    if (!menu) return;

    // cerrar otros
    anyMenu.forEach(m => {
      if (m !== menu) m.classList.remove("product-card__menu-dropdown--active");
    });

    menu.classList.toggle("product-card__menu-dropdown--active");
  });
}

/* ===============================
   SIDEBAR DE COMENTARIOS
================================ */
function initSidebar() {
  const container = document.querySelector(".comments-userss-container");
  if (!container) return;

  const sidebar = container.querySelector(".comments-users-sidebar");
  const overlay = document.querySelector(".comments-overlay");
  const closeBtn = container.querySelector(".comments-users-sidebar__close-btn");
  const commentsList = container.querySelector("#commentsList");
  const form = container.querySelector("#commentForm");
  const productInput = container.querySelector("#producto_id");

  function openSidebar() {
    sidebar.classList.add("comments-users-sidebar--active");
    overlay.classList.add("comments-overlay--active");
  }

  function closeSidebar() {
    sidebar.classList.remove("comments-users-sidebar--active");
    overlay.classList.remove("comments-overlay--active");
    commentsList.innerHTML = "";
    form.reset();
  }

  closeBtn.addEventListener("click", closeSidebar);
  overlay.addEventListener("click", closeSidebar);

  // abrir desde el menú
  document.addEventListener("click", async (e) => {
    const btn = e.target.closest('[data-action="open-comments"]');
    if (!btn) return;

    e.preventDefault();

    const productId = btn.dataset.productId;
    if (!productId) return;

    productInput.value = productId;
    commentsList.innerHTML = "<p>Cargando comentarios...</p>";

    const comentarios = await obtenerComentarios(productId);
    renderComentarios(commentsList, comentarios);
    openSidebar();
  });

  // submit comentario
  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const productId = productInput.value;
    const texto = form.querySelector('textarea[name="texto"]').value.trim();
    if (!productId || !texto) return;

    const res = await enviarComentario(productId, texto);
    if (!res?.success) return;

    const comentarios = await obtenerComentarios(productId);
    renderComentarios(commentsList, comentarios);
    form.reset();
  });
}

/* ===============================
   AJAX
================================ */
function getCSRFToken() {
  const input = document.querySelector('[name=csrfmiddlewaretoken]');
  return input ? input.value : "";
}

async function enviarComentario(productId, texto) {
  const res = await fetch(`/comentarios/crear/${productId}/`, {
    method: "POST",
    headers: {
      "X-CSRFToken": getCSRFToken(),
      "X-Requested-With": "XMLHttpRequest",
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ texto })
  });
  return await res.json();
}

async function obtenerComentarios(productId) {
  const res = await fetch(`/comentarios/obtener/${productId}/`);
  return await res.json();
}

function renderComentarios(container, comentarios) {
  container.innerHTML = comentarios.length === 0
    ? "<p>No hay comentarios aún.</p>"
    : comentarios.map(c => `
        <div class="seller-comments__item">
          <p class="seller-comments__user">${c.usuario} • ${c.fecha}</p>
          <p class="seller-comments__text">${c.texto}</p>
        </div>
      `).join("");
}