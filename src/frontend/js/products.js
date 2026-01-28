/**
 * Products Page Logic
 * 
 * Handles product listing, filtering, and pagination.
 */

// State
let currentPage = 1;
let currentFilters = {
    limit: 50,
    offset: 0,
    search: '',
    chip_brand: '',
    store: '',
    min_price: '',
    max_price: '',
    sort_by: 'price',
    sort_order: 'asc'
};

// Elements
const grid = document.getElementById('productsGrid');
const searchInput = document.getElementById('searchInput');
const chipFilter = document.getElementById('chipFilter');
const storeFilter = document.getElementById('storeFilter');
const minPriceInput = document.getElementById('minPrice');
const maxPriceInput = document.getElementById('maxPrice');
const applyFiltersBtn = document.getElementById('applyFiltersBtn');
const sortSelect = document.getElementById('sortSelect');

// Debounce helper
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

document.addEventListener('DOMContentLoaded', () => {
    // Initialize filters from URL
    const urlParams = new URLSearchParams(window.location.search);
    currentFilters.search = urlParams.get('search') || '';

    // Bind Events
    if (applyFiltersBtn) {
        applyFiltersBtn.addEventListener('click', () => {
            currentPage = 1;
            loadProducts();
        });
    }

    if (searchInput) {
        searchInput.value = currentFilters.search;
        searchInput.addEventListener('input', debounce(() => {
            currentPage = 1;
            loadProducts();
        }, 500));
    }

    if (sortSelect) {
        sortSelect.addEventListener('change', () => {
            const [by, order] = sortSelect.value.split('-');
            currentFilters.sort_by = by;
            currentFilters.sort_order = order;
            loadProducts();
        });
    }

    // Initial Load
    loadProducts();
});

/**
 * Gather filters and fetch products
 */
async function loadProducts() {
    showLoading(grid);

    // Update state from inputs
    if (chipFilter) currentFilters.chip_brand = chipFilter.value;
    if (storeFilter) currentFilters.store = storeFilter.value;
    if (minPriceInput) currentFilters.min_price = minPriceInput.value;
    if (maxPriceInput) currentFilters.max_price = maxPriceInput.value;
    if (searchInput) currentFilters.search = searchInput.value;

    // Calculate offset
    currentFilters.offset = (currentPage - 1) * currentFilters.limit;

    try {
        // Construct params object, removing empty strings
        const params = {};
        for (const [key, value] of Object.entries(currentFilters)) {
            if (value !== '' && value !== null && value !== undefined) {
                params[key] = value;
            }
        }

        // Use search endpoint if query exists, else use list endpoint
        // NOTE: Backend list endpoint now supports filters too, but search is specific for text
        let products = [];
        if (params.search && params.search.length > 0) {
            products = await api.searchProducts({
                query: params.search,
                ...params
            });
        } else {
            // Remove 'search' from params if empty to avoid sending it to list endpoint
            delete params.search;
            products = await api.getProducts(params);
        }

        renderProducts(products);

    } catch (error) {
        console.error("Error loading products:", error);
        showError(grid, 'Erro ao carregar produtos. Tente novamente.');
    }
}

/**
 * Render product cards
 */
function renderProducts(products) {
    if (!products || products.length === 0) {
        grid.innerHTML = `
            <div class="empty-state">
                <p>Nenhum produto encontrado com os filtros selecionados.</p>
            </div>`;
        return;
    }

    grid.innerHTML = products.map(product => {
        const storeBadgeClass = `badge-${product.store.toLowerCase()}`;
        const chipBadgeClass = `badge-${product.chip_brand ? product.chip_brand.toLowerCase() : 'unknown'}`;
        const priceFormatted = formatCurrency(product.price);

        // Handle date
        const scannedDate = new Date(product.scraped_at);
        const dateStr = scannedDate.toLocaleDateString('pt-BR');

        return `
            <div class="product-card">
                <div class="product-header">
                    <span class="badge ${storeBadgeClass}">${product.store}</span>
                    <span class="badge ${chipBadgeClass}">${product.chip_brand || 'N/A'}</span>
                </div>
                
                <h3 class="product-title" title="${product.title}">
                    <a href="${product.url}" target="_blank">${product.title}</a>
                </h3>
                
                <div class="product-info">
                    <p class="product-manufacturer">${product.manufacturer || '-'}</p>
                    <p class="product-model">${product.model || '-'}</p>
                </div>
                
                <div class="product-meta">
                    <span class="scanned-date">Atualizado em: ${dateStr}</span>
                </div>

                <div class="product-footer">
                    <div class="price-container">
                        <span class="product-price">${priceFormatted}</span>
                    </div>
                    <a href="${product.url}" target="_blank" class="btn btn-sm btn-primary">
                        Ver Oferta
                    </a>
                </div>
            </div>
        `;
    }).join('');
}
