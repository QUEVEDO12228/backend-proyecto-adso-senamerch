document.addEventListener("DOMContentLoaded", () => {

    const button = document.querySelector(".sales-made-details__button--download");
    if (!button) return;

    button.addEventListener("click", () => {

        const { jsPDF } = window.jspdf;
        const doc = new jsPDF();

        // Logo opcional
        const imgLogo = new Image();
        imgLogo.src = "/static/assets/img/logo.png";

        imgLogo.onload = () => generatePDF();
        imgLogo.onerror = () => generatePDF(); // si no existe logo, igual generamos PDF

        function generatePDF() {
            // Si logo existe, dibujarlo
            if (imgLogo.complete && imgLogo.naturalWidth !== 0) {
                doc.addImage(imgLogo, "PNG", 10, 10, 40, 20);
            }

            doc.setFontSize(14);
            doc.text("Factura del Pedido", 10, 40);

            // Tabla de productos
            const productCards = document.querySelectorAll(".sales-made-details__product-card");
            const rows = [];

            productCards.forEach(card => {
                const ps = card.querySelectorAll("p");
                let producto = "", cantidad = "", precio = "", descuento = "0%", total = "";

                ps.forEach(p => {
                    const text = p.innerText;
                    if (text.startsWith("Producto:")) producto = text.replace("Producto: ", "").trim();
                    if (text.startsWith("Cantidad:")) cantidad = text.replace("Cantidad: ", "").trim();
                    if (text.startsWith("Precio unitario:")) precio = text.replace("Precio unitario: $", "").trim();
                    if (text.startsWith("Descuento:")) descuento = text.replace("Descuento: ", "").trim();
                    if (text.startsWith("Total con descuento:")) total = text.replace("Total con descuento: $", "").trim();
                    if (text.startsWith("Total:")) total = text.replace("Total: $", "").trim();
                });

                // Si no hay total calculado, multiplicar precio x cantidad
                if (!total) {
                    total = (parseFloat(precio.replace(/,/g, '')) * parseFloat(cantidad)).toFixed(2);
                }

                rows.push({ producto, cantidad, precio, descuento, total });
            });

            const columns = ["Producto", "Cantidad", "Precio Unitario", "Descuento", "Total"];
            const body = rows.map(r => [r.producto, r.cantidad, r.precio, r.descuento, r.total]);

            doc.autoTable({
                startY: 50,
                head: [columns],
                body: body,
                styles: { fontSize: 10 },
                headStyles: { fillColor: [41, 128, 185], textColor: 255 },
                theme: "striped",
                margin: { left: 10, right: 10 }
            });

            // Total pagado
            const totalPagoElem = document.querySelector(".sales-made-details__totals p");
            let totalPago = "0.00";
            if (totalPagoElem) {
                totalPago = totalPagoElem.innerText.replace("Total pagado: $", "").trim();
            }

            const finalY = doc.lastAutoTable.finalY + 10 || 100;
            doc.setFontSize(12);
            doc.text(`Total pagado: $${totalPago}`, 10, finalY);

            doc.save("pedido.pdf");
        }
    });
});