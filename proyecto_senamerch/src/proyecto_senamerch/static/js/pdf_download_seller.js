document.addEventListener("DOMContentLoaded", () => {

    const button = document.querySelector(".sales-made-details__button--download");
    if (!button) return;

    button.addEventListener("click", (e) => {

        e.preventDefault();

        if (button.dataset.clicked === "true") return;
        button.dataset.clicked = "true";

        const { jsPDF } = window.jspdf;
        const doc = new jsPDF();

        const primary = [7, 44, 14]; // Verde principal
        const dark = [40, 40, 40];
        const lightGray = [240, 240, 240];
        const borderGreen = [82, 214, 103]; // Borde siempre
        const borderWidth = 0.5; // Borde 0.5 px

        // ============================
        // LOGO TIPO NAVBAR
        // ============================
        function drawSenaMerch(doc, x, y) {
            const letters = ["S", "e", "n", "a", "M", "e", "r", "c", "h"];
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

            doc.setLineWidth(borderWidth);
            doc.setDrawColor(...borderGreen);
            doc.rect(0, 0, 210, 35); // Borde del header

            drawSenaMerch(doc, 15, 22);

            doc.setTextColor(255, 255, 255);
            doc.setFontSize(10);
            doc.text("Resumen de venta", 195, 18, { align: "right" });

            // ============================
            // INFO TIENDA, VENDEDOR, CLIENTE
            // ============================
            y = 45;

            const storeInfo = [
                "Tienda",
                "Nombre Tienda: LA LOLAfea",
                "Teléfono: 3102973825",
                "Correo: vendedor3senamerch@gmai.com"
            ];

            const vendedorInfo = [
                "Vendedor",
                "Nombre: Emanuel Quevedo Escobar",
                "Correo: vendedor3senamerch@gmai.com"
            ];

            const clienteInfo = [
                "Cliente",
                "Nombre: Jeferson Alexis Duque",
                "Correo: neithanmateo12@gmail.com"
            ];

            // Unir toda la info
            const allInfo = [...storeInfo, ...vendedorInfo, ...clienteInfo];

            // Ajustar alto de la caja dinámicamente (6px por línea + 6px entre secciones)
            const boxHeight = allInfo.length * 6 + 12; // 12px total entre secciones

            doc.setFillColor(...lightGray);
            doc.rect(15, y - 5, 180, boxHeight, "F");

            doc.setLineWidth(borderWidth);
            doc.setDrawColor(...borderGreen);
            doc.rect(15, y - 5, 180, boxHeight); // Borde verde

            doc.setTextColor(...dark);
            doc.setFontSize(10);

            let currentY = y;

            // Colocar la información de Tienda
            storeInfo.forEach(line => {
                doc.text(line.trim(), 20, currentY);
                currentY += 6;
            });

            // Pequeño espacio entre Tienda y Vendedor
            currentY += 6;

            // Colocar la información de Vendedor
            vendedorInfo.forEach(line => {
                doc.text(line.trim(), 20, currentY);
                currentY += 6;
            });

            // Pequeño espacio entre Vendedor y Cliente
            currentY += 6;

            // Colocar la información de Cliente
            clienteInfo.forEach(line => {
                doc.text(line.trim(), 20, currentY);
                currentY += 6;
            });

            y += boxHeight + 5;

            // ============================
            // TABLA PRODUCTOS (VENDEDOR)
            // ============================
            const productCards = document.querySelectorAll(".sales-made-details__product-card");
            const rows = [];

            let totalGeneral = 0;

            productCards.forEach(card => {
                const ps = card.querySelectorAll("p");

                let producto = "", cantidad = 0, precio = 0, total = 0, descuento = 0;

                ps.forEach(p => {
                    const text = p.innerText;

                    if (text.startsWith("Producto:"))
                        producto = text.replace("Producto:", "").trim();

                    if (text.startsWith("Cantidad:"))
                        cantidad = parseFloat(text.replace("Cantidad:", "").trim());

                    if (text.startsWith("Precio unitario:"))
                        precio = parseFloat(text.replace("Precio unitario: $", "").trim());

                    if (text.startsWith("Descuento:"))
                        descuento = parseFloat(text.replace("Descuento:", "").replace("%", "").trim());

                    if (text.startsWith("Total con descuento:"))
                        total = parseFloat(text.replace("Total con descuento: $", "").trim());

                    if (text.startsWith("Total:"))
                        total = parseFloat(text.replace("Total: $", "").trim());
                });

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
                    textColor: [255, 255, 255],
                    halign: "center"
                },
                alternateRowStyles: {
                    fillColor: [245, 255, 245]
                },
                didDrawCell: function (data) {
                    doc.setLineWidth(borderWidth);
                    doc.setDrawColor(...borderGreen);
                    doc.rect(data.cell.x, data.cell.y, data.cell.width, data.cell.height);
                }
            });

            // ============================
            // RESUMEN FINANCIERO
            // ============================
            let finalY = doc.lastAutoTable.finalY + 12;

            doc.setFillColor(...primary);
            doc.roundedRect(120, finalY, 75, 22, 3, 3, "F");

            doc.setLineWidth(borderWidth);
            doc.setDrawColor(...borderGreen);
            doc.roundedRect(120, finalY, 75, 22, 3, 3); // borde redondeado

            doc.setTextColor(255, 255, 255);
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