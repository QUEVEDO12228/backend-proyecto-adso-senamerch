document.addEventListener("DOMContentLoaded", () => {

    const button = document.querySelector(".sales-made-details__button--download");
    if (!button) return;

    button.addEventListener("click", (e) => {

        e.preventDefault();

        // Evita doble ejecución
        if (button.dataset.clicked === "true") return;
        button.dataset.clicked = "true";

        const { jsPDF } = window.jspdf;
        const doc = new jsPDF();

        const imgLogo = new Image();
        imgLogo.src = "/static/assets/img/logo.png";

        imgLogo.onload = () => generatePDF();
        imgLogo.onerror = () => generatePDF();

        function generatePDF() {

            let y = 20;

            if (imgLogo.complete && imgLogo.naturalWidth !== 0) {
                doc.addImage(imgLogo, "PNG", 10, 10, 40, 20);
                y = 40;
            }

            doc.setFontSize(16);
            doc.text("Factura del Pedido", 10, y);

            const productCards = document.querySelectorAll(".sales-made-details__product-card");
            const rows = [];

            productCards.forEach(card => {

                const ps = card.querySelectorAll("p");

                let producto="", cantidad="", precio="", descuento="0%", total="";

                ps.forEach(p => {
                    const text = p.innerText;

                    if (text.startsWith("Producto:"))
                        producto = text.replace("Producto:", "").trim();

                    if (text.startsWith("Cantidad:"))
                        cantidad = text.replace("Cantidad:", "").trim();

                    if (text.startsWith("Precio unitario:"))
                        precio = text.replace("Precio unitario: $", "").trim();

                    if (text.startsWith("Descuento:"))
                        descuento = text.replace("Descuento:", "").trim();

                    if (text.startsWith("Total con descuento:"))
                        total = text.replace("Total con descuento: $", "").trim();

                    if (text.startsWith("Total:"))
                        total = text.replace("Total: $", "").trim();
                });

                if (!total && precio && cantidad) {
                    total = (parseFloat(precio) * parseFloat(cantidad)).toFixed(2);
                }

                rows.push([producto, cantidad, precio, descuento, total]);

            });

            doc.autoTable({
                startY: y + 10,
                head: [["Producto","Cantidad","Precio","Descuento","Total"]],
                body: rows,
                theme: "striped"
            });

            doc.save("pedido.pdf");

            // Reactivar botón después
            setTimeout(() => {
                button.dataset.clicked = "false";
            }, 1000);
        }

    });

});