document.addEventListener("DOMContentLoaded", () => {

    const button = document.querySelector(".sales-made-details__button--download");
    if (!button) return;

    button.addEventListener("click", (e) => {

        e.preventDefault();

        const { jsPDF } = window.jspdf;
        const doc = new jsPDF();

        const primary = [7, 44, 14];
        const borderGreen = [82, 214, 103];
        const lightGray = [240, 240, 240];
        const dark = [40, 40, 40];
        const borderWidth = 0.5;

        // 🔥 LIMPIAR NÚMEROS
        function cleanNumber(text) {
            if (!text) return 0;

            return parseFloat(
                text.replace(/\./g, "")
                    .replace(",", ".")
                    .replace(/[^\d.-]/g, "")
            ) || 0;
        }

        // 🔥 EXTRAER TEXTO POR LABEL (SIN IDS)
        function getValue(label, container) {
            const elements = container.querySelectorAll("p");

            for (let el of elements) {
                if (el.innerText.includes(label)) {
                    return el.innerText.split(":")[1]?.trim() || "-";
                }
            }

            return "-";
        }

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

            // HEADER
            doc.setFillColor(...primary);
            doc.rect(0, 0, 210, 35, "F");

            doc.setDrawColor(...borderGreen);
            doc.setLineWidth(borderWidth);
            doc.rect(0, 0, 210, 35);

            drawSenaMerch(doc, 15, 22);

            doc.setTextColor(255, 255, 255);
            doc.setFontSize(10);
            doc.text("Comprobante de compra", 195, 18, { align: "right" });

            // 🔥 CONTENEDORES
            const sidebar = document.querySelector(".sales-made-details__sidebar");

            // INFO REAL
            const storeInfo = [
                "Tienda",
                `Nombre Tienda: ${getValue("Nombre Tienda", sidebar)}`,
                `Teléfono: ${getValue("Teléfono", sidebar)}`,
                `Correo: ${getValue("Correo", sidebar)}`
            ];

            const vendedorInfo = [
                "Vendedor",
                `Nombre: ${getValue("Nombre", sidebar)}`,
                `Correo: ${getValue("Correo", sidebar)}`
            ];

            const allInfo = [...storeInfo, ...vendedorInfo];
            const boxHeight = allInfo.length * 6 + 10;

            y = 45;

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

            y += boxHeight + 5;

            // 🔥 PRODUCTOS
            const productCards = document.querySelectorAll(".sales-made-details__product-card");

            const rows = [];
            let totalGeneral = 0;

            productCards.forEach(card => {

                const producto = getValue("Producto", card);
                const cantidad = cleanNumber(getValue("Cantidad", card));
                const precio = cleanNumber(getValue("Precio unitario", card));
                const descuento = cleanNumber(getValue("Descuento", card));

                let total = cleanNumber(getValue("Total con descuento", card));
                if (!total) {
                    total = cleanNumber(getValue("Total", card));
                }

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
                head: [["Producto", "Cantidad", "Descuento", "Precio", "Total"]],
                body: rows,
                theme: "grid",
                styles: {
                    fontSize: 9,
                    halign: "center"
                },
                headStyles: {
                    fillColor: primary,
                    textColor: [255, 255, 255]
                }
            });

            // TOTAL
            let finalY = doc.lastAutoTable.finalY + 12;

            doc.setFillColor(...primary);
            doc.roundedRect(120, finalY, 75, 22, 3, 3, "F");

            doc.setTextColor(255, 255, 255);
            doc.text("Total pagado", 157, finalY + 8, { align: "center" });

            doc.text(`$${totalGeneral.toFixed(2)}`, 157, finalY + 16, { align: "center" });

            // SAVE
            doc.save("comprobante_compra.pdf");
        }

        generatePDF();
    });
});