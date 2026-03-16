document.addEventListener("DOMContentLoaded", () => {

  const form = document.getElementById("formComentario");
  const lista = document.getElementById("listaComentarios");

  if (!form || !lista) return;

  const productId = form.dataset.productoId;

  // Detectar vista vendedor o cliente
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

  // ==========================
  // CREAR COMENTARIO
  // ==========================
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


  // ==========================
  // CARGAR COMENTARIOS
  // ==========================
  async function cargarComentarios() {

    const res = await fetch(`/comentarios/obtener/${productId}/`);
    const comentarios = await res.json();

    renderComentarios(comentarios);

  }


  // ==========================
  // RENDER COMENTARIOS
  // ==========================
  function renderComentarios(comentarios) {

    if (comentarios.length === 0) {
      lista.innerHTML = "<p>No hay comentarios aún.</p>";
      return;
    }

    lista.innerHTML = comentarios.map(c => `

      <div class="${classes.item}" data-id="${c.id}">

        <p class="${classes.user}">
          ${c.usuario} • ${c.fecha}
        </p>

        <p class="${classes.text}">
          ${c.texto}
        </p>

        ${c.es_mio ? `
          <div class="comment-actions">

            <button class="edit-comment">
              ✏ Editar
            </button>

            <button class="delete-comment">
              🗑 Eliminar
            </button>

          </div>
        ` : ""}

      </div>

    `).join("");

  }


  // ==========================
  // EVENTOS EDITAR / ELIMINAR
  // ==========================
  lista.addEventListener("click", async (e) => {

    const item = e.target.closest("[data-id]");
    if (!item) return;

    const id = item.dataset.id;


    // ==========================
    // ELIMINAR
    // ==========================
    if (e.target.classList.contains("delete-comment")) {

      if (!confirm("¿Eliminar este comentario?")) return;

      const res = await fetch(`/comentarios/eliminar/${id}/`, {
        method: "POST",
        headers: {
          "X-CSRFToken": getCSRFToken(),
          "X-Requested-With": "XMLHttpRequest"
        }
      });

      const data = await res.json();

      if (data.success) {
        item.remove();
      }

    }


    // ==========================
    // EDITAR
    // ==========================
    if (e.target.classList.contains("edit-comment")) {

      const textEl = item.querySelector(`.${classes.text}`);
      const textoActual = textEl.innerText;

      const nuevoTexto = prompt("Editar comentario:", textoActual);

      if (!nuevoTexto || nuevoTexto.trim() === textoActual) return;

      const res = await fetch(`/comentarios/editar/${id}/`, {
        method: "POST",
        headers: {
          "X-CSRFToken": getCSRFToken(),
          "X-Requested-With": "XMLHttpRequest",
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          texto: nuevoTexto.trim()
        })
      });

      const data = await res.json();

      if (data.success) {
        textEl.innerText = data.texto;
      }

    }

  });


  // ==========================
  // CSRF TOKEN
  // ==========================
  function getCSRFToken() {

    const input = document.querySelector('[name=csrfmiddlewaretoken]');
    return input ? input.value : "";

  }

});