/**
 * Dashboard JavaScript
 * 
 * Handles dashboard page functionality
 */

// Load dashboard data on page load
// Load dashboard data on page load
document.addEventListener('DOMContentLoaded', async () => {
    // Attach event listeners first
    const btnRunScraper = document.getElementById('btnRunScraper');
    if (btnRunScraper) {
        btnRunScraper.addEventListener('click', runScraper);
    }

    // Load data
    loadDashboardData();
    loadBestDeals();
    loadRecentActivity();
});

/**
 * Load main dashboard statistics
 */
async function loadDashboardData() {
    try {
        const stats = await api.getStats();

        // Update total products
        document.getElementById('totalProducts').textContent =
            stats.total_products?.toLocaleString('pt-BR') || '0';

        // Update average price
        document.getElementById('avgPrice').textContent =
            formatCurrency(stats.average_price || 0);

        // Update best deals count
        document.getElementById('bestDeals').textContent =
            stats.best_deals_count || '0';

        // Update last update time
        if (stats.latest_scrape) {
            document.getElementById('lastUpdate').textContent =
                formatRelativeTime(stats.latest_scrape);
        }
    } catch (error) {
        console.error('Failed to load dashboard data:', error);
        showToast('Erro ao carregar estatísticas', 'error');
    }
}

/**
 * Load best deals preview
 */
async function loadBestDeals() {
    const grid = document.getElementById('bestDealsGrid');

    try {
        const products = await api.getBestDeals(3);

        if (products.length === 0) {
            grid.innerHTML = '<p class="empty-state">Nenhuma oferta encontrada</p>';
            return;
        }

        grid.innerHTML = products.map(product => createProductCard(product)).join('');
    } catch (error) {
        console.error('Failed to load best deals:', error);
        showError(grid, 'Erro ao carregar ofertas');
    }
}

/**
 * Load recent activity
 */
async function loadRecentActivity() {
    const list = document.getElementById('activityList');

    try {
        const history = await api.getScraperHistory(5);

        if (!history.runs || history.runs.length === 0) {
            list.innerHTML = '<p class="empty-state">Nenhuma atividade recente</p>';
            return;
        }

        list.innerHTML = history.runs.map(run => createActivityItem(run)).join('');
    } catch (error) {
        console.error('Failed to load activity:', error);
        // Keep default activity item on error
    }
}

/**
 * Create product card HTML
 */
function createProductCard(product) {
    const storeBadgeClass = `badge-${product.store.toLowerCase()}`;
    const chipBadgeClass = `badge-${product.chip_brand.toLowerCase()}`;

    return `
        <div class="product-card">
            <div class="product-header">
                <span class="badge ${storeBadgeClass}">${product.store}</span>
                <span class="badge ${chipBadgeClass}">${product.chip_brand}</span>
            </div>
            <h3 class="product-title">${product.title}</h3>
            <div class="product-info">
                <p class="product-manufacturer">${product.manufacturer}</p>
                <p class="product-model">${product.model}</p>
            </div>
            <div class="product-footer">
                <p class="product-price">${formatCurrency(product.price)}</p>
                <a href="${product.url}" target="_blank" class="btn btn-sm btn-primary">
                    Ver Oferta
                </a>
            </div>
        </div>
    `;
}

/**
 * Create activity item HTML
 */
function createActivityItem(run) {
    const iconClass = run.success ? 'activity-icon-success' : 'activity-icon-error';
    const icon = run.success ?
        '<path d="M5 13l4 4L19 7"/>' :
        '<path d="M6 18L18 6M6 6l12 12"/>';

    const title = run.success ?
        `Scraper executado com sucesso - ${run.products_saved} produtos salvos` :
        `Scraper falhou - ${run.store}`;

    return `
        <div class="activity-item">
            <div class="activity-icon ${iconClass}">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    ${icon}
                </svg>
            </div>
            <div class="activity-content">
                <p class="activity-title">${title}</p>
                <p class="activity-time">${formatRelativeTime(run.started_at)}</p>
            </div>
        </div>
    `;
}

/**
 * Run scraper
 */
async function runScraper(event) {
    const button = event.currentTarget;
    const originalText = button.innerHTML;

    // Show loading state
    button.disabled = true;
    button.innerHTML = `
        <svg class="spinner" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <circle cx="12" cy="12" r="10" stroke-width="4" opacity="0.25"/>
            <path d="M12 2a10 10 0 0110 10" stroke-width="4"/>
        </svg>
        Executando...
    `;

    try {
        const result = await api.runScrapers(['Pichau', 'Kabum', 'Terabyte']);

        showToast(
            `Scraper executado! ${result.total_products_saved} produtos salvos`,
            'success'
        );

        // Reload dashboard data
        await loadDashboardData();
        await loadBestDeals();
        await loadRecentActivity();
    } catch (error) {
        console.error('Failed to run scraper:', error);
        showToast('Erro ao executar scraper', 'error');
    } finally {
        button.disabled = false;
        button.innerHTML = originalText;
    }
}
