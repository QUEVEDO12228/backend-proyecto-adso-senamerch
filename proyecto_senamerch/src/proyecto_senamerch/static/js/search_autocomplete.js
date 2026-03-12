document.addEventListener("DOMContentLoaded", function(){

    const searchInput = document.getElementById("searchInput");
    const suggestionsBox = document.getElementById("searchSuggestions");
    const cards = document.querySelectorAll(".product-card");

    if(!searchInput || !suggestionsBox) return;

    const url = suggestionsBox.dataset.url;

    let selectedIndex = -1;

    /* ===================== */
    /* NORMALIZAR TEXTO      */
    /* ===================== */

    function normalizeText(text){

        return text
        .toLowerCase()
        .normalize("NFD")
        .replace(/[\u0300-\u036f]/g,"");

    }

    /* ===================== */
    /* FILTRAR PRODUCTOS     */
    /* ===================== */

    function filterCards(query){

        const queryNormalized = normalizeText(query);

        cards.forEach(card => {

            const nombre = normalizeText(card.dataset.nombre || "");
            const tienda = normalizeText(card.dataset.tienda || "");
            const categoria = normalizeText(card.dataset.categoria || "");
            const precio = normalizeText(card.dataset.precio || "");

            if(
                nombre.includes(queryNormalized) ||
                tienda.includes(queryNormalized) ||
                categoria.includes(queryNormalized) ||
                precio.includes(queryNormalized)
            ){
                card.style.display = "block";
            }else{
                card.style.display = "none";
            }

        });

    }

    /* ===================== */
    /* AUTOCOMPLETE          */
    /* ===================== */

    searchInput.addEventListener("keyup", function(){

        const query = this.value;

        filterCards(query);

        if(query.length < 2){
            suggestionsBox.innerHTML = "";
            return;
        }

        fetch(`${url}?q=${query}`)
        .then(res => res.json())
        .then(data => {

            let html = "";

            /* PRODUCTOS */

            if(data.productos && data.productos.length > 0){

                html += "<div class='suggestion-group'>Productos</div>";

                data.productos.forEach(p => {

                    html += `
                    <div class="suggestion-item" data-value="${p.nombre}">

                        <div class="suggestion-product">

                            <img src="${p.imagen}" class="suggestion-img">

                            <div class="suggestion-info">

                                <div class="suggestion-name">${p.nombre}</div>

                                <div class="suggestion-meta">

                                    <span class="suggestion-category">${p.categoria}</span>
                                    <span class="suggestion-price">$${p.precio}</span>

                                </div>

                            </div>

                        </div>

                    </div>
                    `;

                });

            }

            /* TIENDAS */

            if(data.tiendas && data.tiendas.length > 0){

                html += "<div class='suggestion-group'>Tiendas</div>";

                data.tiendas.forEach(t => {

                    html += `
                    <div class="suggestion-item">
                        🏪 ${t.nombre}
                    </div>
                    `;

                });

            }

            suggestionsBox.innerHTML = html;

            addSuggestionEvents();

        })
        .catch(error => {
            console.error("Error en autocomplete:", error);
        });

    });

    /* ===================== */
    /* CLICK EN SUGERENCIA   */
    /* ===================== */

    function addSuggestionEvents(){

        const items = document.querySelectorAll(".suggestion-item");

        items.forEach((item,index)=>{

            item.addEventListener("click",function(){

                const texto = this.dataset.value.toLowerCase();

                searchInput.value = texto;

                suggestionsBox.innerHTML = "";

                filterCards(texto);

            });

        });

    }

    /* ===================== */
    /* NAVEGACIÓN TECLADO    */
    /* ===================== */

    searchInput.addEventListener("keydown", function(e){

        const items = document.querySelectorAll(".suggestion-item");

        if(!items.length) return;

        if(e.key === "ArrowDown"){

            selectedIndex++;

            if(selectedIndex >= items.length){
                selectedIndex = 0;
            }

            highlightItem(items);

        }

        if(e.key === "ArrowUp"){

            selectedIndex--;

            if(selectedIndex < 0){
                selectedIndex = items.length - 1;
            }

            highlightItem(items);

        }

        if(e.key === "Enter"){

            if(selectedIndex >= 0){

                const texto = items[selectedIndex].dataset.value.toLowerCase();

                searchInput.value = texto;

                suggestionsBox.innerHTML = "";

                filterCards(texto);

            }

        }

    });

    /* ===================== */
    /* RESALTAR ITEM         */
    /* ===================== */

    function highlightItem(items){

        items.forEach(item=>{
            item.classList.remove("active");
        });

        if(items[selectedIndex]){
            items[selectedIndex].classList.add("active");
        }

    }

    /* ===================== */
    /* CERRAR TOOLTIP        */
    /* ===================== */

    document.addEventListener("click", function(e){

        if(!e.target.closest(".search-bar")){
            suggestionsBox.innerHTML = "";
        }

    });

});