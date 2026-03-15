document.addEventListener("DOMContentLoaded", () => {

  const form = document.getElementById("formComentario");
  const lista = document.getElementById("listaComentarios");

  if (!form || !lista) return;

  const productId = form.dataset.productoId;

  // Detectar si estamos en vista vendedor o cliente
  const isSellerView = document.querySelector(".seller-comments");

  const classes = isSellerView
    ? {
        item: "seller-comments__item",
        user: "seller-comments__user",
        text: "seller-comments__text"
      }
    : {
        item: "comments__item",
        user: "comments__user",
        text: "comments__text"
      };

  cargarComentarios();

  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const textarea = form.querySelector("textarea[name='texto']");
    const texto = textarea.value.trim();

    if (!texto) return;

    const res = await fetch(`/comentarios/crear/${productId}/`, {
      method: "POST",
      headers: {
        "X-CSRFToken": getCSRFToken(),
        "X-Requested-With": "XMLHttpRequest",
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ texto })
    });

    const data = await res.json();

    if (data.success) {
      textarea.value = "";
      cargarComentarios();
    }

  });

  async function cargarComentarios() {

    const res = await fetch(`/comentarios/obtener/${productId}/`);
    const comentarios = await res.json();

    renderComentarios(comentarios);
  }

  function renderComentarios(comentarios) {

    if (comentarios.length === 0) {
      lista.innerHTML = "<p>No hay comentarios aún.</p>";
      return;
    }

    lista.innerHTML = comentarios.map(c => `
      <div class="${classes.item}">
        <p class="${classes.user}">
          ${c.usuario} • ${c.fecha}
        </p>
        <p class="${classes.text}">
          ${c.texto}
        </p>
      </div>
    `).join("");
  }

  function getCSRFToken() {
    const input = document.querySelector('[name=csrfmiddlewaretoken]');
    return input ? input.value : "";
  }

});