document.addEventListener("DOMContentLoaded", () => {

    const button = document.querySelector(".sales-made-details__button--download");
    if (!button) return;

    button.addEventListener("click", (e) => {

        e.preventDefault();

        if (button.dataset.clicked === "true") return;
        button.dataset.clicked = "true";

        const { jsPDF } = window.jspdf;
        const doc = new jsPDF();

        const primary = [29, 150, 49];
        const dark = [40, 40, 40];
        const lightGray = [240, 240, 240];

        // ============================
        // LOGO TIPO NAVBAR
        // ============================
        function drawSenaMerch(doc, x, y) {

            const letters = ["S","e","n","a","M","e","r","c","h"];
            let posX = x;

            letters.forEach(letter => {

                doc.setTextColor(140, 233, 155);
                doc.setFontSize(20);

                doc.text(letter, posX - 0.3, y);
                doc.text(letter, posX + 0.3, y);
                doc.text(letter, posX, y - 0.3);
                doc.text(letter, posX, y + 0.3);

                doc.setTextColor(255, 255, 255);
                doc.text(letter, posX, y);

                posX += 6;
            });
        }

        // ============================
        // GENERAR PDF
        // ============================
        function generatePDF() {

            let y = 20;

            // ============================
            // HEADER
            // ============================
            doc.setFillColor(...primary);
            doc.rect(0, 0, 210, 35, "F");

            drawSenaMerch(doc, 15, 22);

            doc.setTextColor(255,255,255);
            doc.setFontSize(10);
            doc.text("Resumen de venta", 195, 18, { align: "right" });

            // ============================
            // INFO GENERAL
            // ============================
            y = 45;

            const now = new Date();
            const fecha = now.toLocaleDateString();
            const hora = now.toLocaleTimeString();

            const orderTitle = document.querySelector(".sales-made-details__title").innerText;

            doc.setTextColor(...dark);
            doc.setFontSize(12);
            doc.text("DETALLE DE VENTA", 15, y);

            y += 8;

            doc.setFontSize(10);
            doc.text(orderTitle, 15, y);
            doc.text(`Fecha: ${fecha}`, 140, y);

            y += 6;
            doc.text(`Hora: ${hora}`, 140, y);

            const numeroVenta = "VENTA-" + String(Math.floor(Math.random() * 999999)).padStart(6, "0");

            y += 6;
            doc.text(`N° Venta: ${numeroVenta}`, 140, y);

            y += 10;

            // ============================
            // INFO CLIENTE / TIENDA
            // ============================
            const sidebar = document.querySelector(".sales-made-details__sidebar");
            const lines = sidebar.innerText.split("\n").filter(l => l.trim() !== "");

            doc.setFillColor(...lightGray);
            doc.rect(15, y - 5, 180, 32, "F");

            doc.setFontSize(10);

            let col1Y = y;
            let col2Y = y;

            lines.forEach((line, index) => {

                if (index < Math.ceil(lines.length / 2)) {
                    doc.text(line.trim(), 20, col1Y);
                    col1Y += 6;
                } else {
                    doc.text(line.trim(), 110, col2Y);
                    col2Y += 6;
                }

            });

            y += 38;

            // ============================
            // TABLA PRODUCTOS (VENDEDOR)
            // ============================
            const productCards = document.querySelectorAll(".sales-made-details__product-card");
            const rows = [];

            let totalGeneral = 0;

            productCards.forEach(card => {

                const ps = card.querySelectorAll("p");

                let producto="", cantidad=0, precio=0, total=0;

                ps.forEach(p => {
                    const text = p.innerText;

                    if (text.startsWith("Producto:"))
                        producto = text.replace("Producto:", "").trim();

                    if (text.startsWith("Cantidad:"))
                        cantidad = parseFloat(text.replace("Cantidad:", "").trim());

                    if (text.startsWith("Precio unitario:"))
                        precio = parseFloat(text.replace("Precio unitario: $", "").trim());

                    if (text.startsWith("Total con descuento:"))
                        total = parseFloat(text.replace("Total con descuento: $", "").trim());

                    if (text.startsWith("Total:"))
                        total = parseFloat(text.replace("Total: $", "").trim());
                });

                totalGeneral += total;

                rows.push([
                    producto,
                    cantidad,
                    `$${precio.toFixed(2)}`,
                    `$${total.toFixed(2)}`
                ]);
            });

            doc.autoTable({
                startY: y,
                head: [["Producto","Cantidad","Precio","Ingreso"]],
                body: rows,
                theme: "grid",
                styles: {
                    fontSize: 9,
                    cellPadding: 3
                },
                headStyles: {
                    fillColor: primary,
                    textColor: [255,255,255],
                    halign: "center"
                },
                bodyStyles: {
                    halign: "center"
                },
                alternateRowStyles: {
                    fillColor: [245, 255, 245]
                }
            });

            // ============================
            // RESUMEN FINANCIERO
            // ============================
            let finalY = doc.lastAutoTable.finalY + 12;

            doc.setFillColor(...primary);
            doc.roundedRect(120, finalY, 75, 22, 3, 3, "F");

            doc.setTextColor(255,255,255);
            doc.setFontSize(10);
            doc.text("Total generado", 157, finalY + 8, { align: "center" });

            doc.setFontSize(12);
            doc.text(`$${totalGeneral.toFixed(2)}`, 157, finalY + 16, { align: "center" });

            // ============================
            // FOOTER
            // ============================
            finalY += 35;

            doc.setDrawColor(...primary);
            doc.line(15, finalY, 195, finalY);

            finalY += 8;

            doc.setFontSize(9);
            doc.setTextColor(100);

            doc.text("Reporte generado para el vendedor", 15, finalY);
            doc.text("SenaMerch - Panel de ventas", 15, finalY + 5);

            doc.setFontSize(8);
            doc.text("© 2026 SenaMerch", 15, finalY + 10);

            // ============================
            // GUARDAR
            // ============================
            doc.save("reporte_venta.pdf");

            setTimeout(() => {
                button.dataset.clicked = "false";
            }, 1000);
        }

        generatePDF();

    });

});