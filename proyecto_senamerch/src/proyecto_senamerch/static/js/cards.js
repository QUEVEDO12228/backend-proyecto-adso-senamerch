// =======================
// OBTENER CSRF TOKEN
// =======================
function getCookie(name) {
  let cookieValue = null;

  if (document.cookie && document.cookie !== "") {
    const cookies = document.cookie.split(";");

    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();

      if (cookie.substring(0, name.length + 1) === name + "=") {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }

  return cookieValue;
}

document.addEventListener("DOMContentLoaded", () => {

  const csrftoken = getCookie("csrftoken");

  // =======================
  // SELECCIONAR TODOS LOS RATINGS
  // =======================
  document.querySelectorAll(".product-card__rating, .details__rating").forEach(rating => {

    const productoId = rating.dataset.producto;
    if (!productoId) return; // Si no tiene producto_id, ignorar

    const stars = rating.querySelectorAll("[data-value]");
    let currentRating = parseInt(rating.dataset.userRating || 0);

    // =======================
    // FUNCION PARA PINTAR ESTRELLAS
    // =======================
    function paintStars(value) {
      stars.forEach(star => {
        const starValue = parseInt(star.dataset.value);
        star.classList.toggle("filled", starValue <= value);
        star.classList.toggle("product-card__star--active", starValue <= value);
      });
    }

    // ESTADO INICIAL
    paintStars(currentRating);

    // =======================
    // EVENTOS POR CADA ESTRELLA
    // =======================
    stars.forEach(star => {
      const value = parseInt(star.dataset.value);

      // HOVER
      star.addEventListener("mouseenter", () => paintStars(value));

      // QUITAR HOVER
      star.addEventListener("mouseleave", () => paintStars(currentRating));

      // CLICK PARA CALIFICAR
      star.addEventListener("click", () => {
        currentRating = value;
        paintStars(currentRating);

        // POST AL BACKEND
        fetch("/products/calificar-producto/", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrftoken
          },
          credentials: "same-origin",
          body: JSON.stringify({
            producto_id: productoId,
            puntuacion: value
          })
        })
        .then(res => res.json())
        .then(data => {
          if (data.success) {
            // Actualizar dataset para que al recargar hover se mantenga
            rating.dataset.userRating = data.puntuacion;
          } else {
            console.error("No se pudo guardar la calificación:", data.error);
          }
        })
        .catch(error => console.error("Error al calificar:", error));
      });

    });

  });

});