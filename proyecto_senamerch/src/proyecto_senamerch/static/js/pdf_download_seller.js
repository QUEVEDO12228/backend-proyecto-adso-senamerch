document.addEventListener("DOMContentLoaded", () => {

    const button = document.querySelector(".sales-made-details__button--download");
    if (!button) return;

    button.addEventListener("click", (e) => {

        e.preventDefault();

        if (button.dataset.clicked === "true") return;
        button.dataset.clicked = "true";

        const { jsPDF } = window.jspdf;
        const doc = new jsPDF();

        // 🎨 COLORES SENAMERCH
        const primary = [7, 44, 14];        // --secundary-950
        const borderGreen = [82, 214, 103]; // --secundary-400
        const lightGray = [240, 240, 240];
        const dark = [40, 40, 40];

        const borderWidth = 0.5;

        // =========================
        // 🔥 LIMPIAR NÚMEROS (FIX REAL)
        // =========================
        function cleanNumber(text) {
            if (!text) return 0;

            return parseFloat(
                text
                    .replace(/\./g, "")
                    .replace(",", ".")
                    .replace(/[^\d.-]/g, "")
            ) || 0;
        }

        // =========================
        // EXTRAER TEXTO
        // =========================
        function getText(id) {
            const el = document.getElementById(id);
            if (!el) return "-";
            return el.innerText.split(":")[1]?.trim() || "-";
        }

        // =========================
        // LOGO SENAMERCH
        // =========================
        function drawSenaMerch(doc, x, y) {
            const letters = ["S","e","n","a","M","e","r","c","h"];
            let posX = x;

            letters.forEach(letter => {
                doc.setTextColor(140, 233, 155);
                doc.setFontSize(20);

                doc.text(letter, posX - 0.4, y);
                doc.text(letter, posX + 0.4, y);
                doc.text(letter, posX, y - 0.4);
                doc.text(letter, posX, y + 0.4);

                doc.setTextColor(255, 255, 255);
                doc.text(letter, posX, y);

                posX += 8;
            });
        }

        function generatePDF() {

            let y = 20;

            // =========================
            // HEADER
            // =========================
            doc.setFillColor(...primary);
            doc.rect(0, 0, 210, 35, "F");

            doc.setDrawColor(...borderGreen);
            doc.setLineWidth(borderWidth);
            doc.rect(0, 0, 210, 35);

            drawSenaMerch(doc, 15, 22);

            doc.setTextColor(255, 255, 255);
            doc.setFontSize(10);
            doc.text("Resumen de venta", 195, 18, { align: "right" });

            // =========================
            // INFO
            // =========================
            y = 45;

            const storeInfo = [
                "Tienda",
                `Nombre Tienda: ${getText("pdf-store-name")}`,
                `Teléfono: ${getText("pdf-store-phone")}`,
                `Correo: ${getText("pdf-store-email")}`
            ];

            const vendedorInfo = [
                "Vendedor",
                `Nombre: ${getText("pdf-seller-name")}`,
                `Correo: ${getText("pdf-seller-email")}`
            ];

            const clienteInfo = [
                "Cliente",
                `Nombre: ${getText("pdf-client-name")}`,
                `Correo: ${getText("pdf-client-email")}`
            ];

            const allInfo = [...storeInfo, ...vendedorInfo, ...clienteInfo];
            const boxHeight = allInfo.length * 6 + 12;

            doc.setFillColor(...lightGray);
            doc.rect(15, y - 5, 180, boxHeight, "F");

            doc.setDrawColor(...borderGreen);
            doc.rect(15, y - 5, 180, boxHeight);

            doc.setTextColor(...dark);
            doc.setFontSize(10);

            let currentY = y;

            storeInfo.forEach(line => {
                doc.text(line, 20, currentY);
                currentY += 6;
            });

            currentY += 6;

            vendedorInfo.forEach(line => {
                doc.text(line, 20, currentY);
                currentY += 6;
            });

            currentY += 6;

            clienteInfo.forEach(line => {
                doc.text(line, 20, currentY);
                currentY += 6;
            });

            y += boxHeight + 5;

            // =========================
            // PRODUCTOS (FIX TOTAL)
            // =========================
            const productCards = document.querySelectorAll(".sales-made-details__product-card");
            const rows = [];

            let totalGeneral = 0;

            productCards.forEach(card => {

                const producto = card.querySelector(".pdf-product-name")?.innerText.split(":")[1]?.trim() || "-";

                const cantidad = cleanNumber(card.querySelector(".pdf-product-qty")?.innerText);

                const precio = cleanNumber(card.querySelector(".pdf-product-price")?.innerText);

                const descuento = cleanNumber(card.querySelector(".pdf-product-discount")?.innerText);

                const total = cleanNumber(card.querySelector(".pdf-product-total")?.innerText);

                totalGeneral += total;

                rows.push([
                    producto,
                    cantidad,
                    descuento > 0 ? `${descuento}%` : "-",
                    `$${precio.toFixed(2)}`,
                    `$${total.toFixed(2)}`
                ]);
            });

            doc.autoTable({
                startY: y,
                head: [["Producto", "Cantidad", "Descuento", "Precio", "Ingreso"]],
                body: rows,
                theme: "grid",
                styles: {
                    fontSize: 9,
                    cellPadding: 3,
                    halign: "center"
                },
                headStyles: {
                    fillColor: primary,
                    textColor: [255, 255, 255]
                },
                alternateRowStyles: {
                    fillColor: [241, 252, 242]
                },
                didDrawCell: function (data) {
                    doc.setDrawColor(...borderGreen);
                    doc.setLineWidth(borderWidth);
                    doc.rect(data.cell.x, data.cell.y, data.cell.width, data.cell.height);
                }
            });

            // =========================
            // TOTAL
            // =========================
            let finalY = doc.lastAutoTable.finalY + 12;

            doc.setFillColor(...primary);
            doc.roundedRect(120, finalY, 75, 22, 3, 3, "F");

            doc.setDrawColor(...borderGreen);
            doc.roundedRect(120, finalY, 75, 22, 3, 3);

            doc.setTextColor(255, 255, 255);
            doc.setFontSize(10);
            doc.text("Total generado", 157, finalY + 8, { align: "center" });

            doc.setFontSize(12);
            doc.text(`$${totalGeneral.toFixed(2)}`, 157, finalY + 16, { align: "center" });

            // =========================
            // FOOTER
            // =========================
            finalY += 35;

            doc.setDrawColor(...primary);
            doc.line(15, finalY, 195, finalY);

            finalY += 8;

            doc.setFontSize(9);
            doc.setTextColor(100);

            doc.text("Reporte generado para el vendedor", 15, finalY);
            doc.text("SenaMerch - Panel de ventas", 15, finalY + 5);
            doc.text("© 2026 SenaMerch", 15, finalY + 10);

            // =========================
            // GUARDAR
            // =========================
            doc.save("reporte_venta.pdf");

            setTimeout(() => {
                button.dataset.clicked = "false";
            }, 1000);
        }

        generatePDF();
    });
});