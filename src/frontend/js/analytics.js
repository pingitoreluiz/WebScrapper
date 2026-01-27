/**
 * Analytics Dashboard Logic
 * 
 * Handles chart rendering and data fetching for the analytics page.
 */

// Global Chart configurations
Chart.defaults.font.family = "'Inter', sans-serif";
Chart.defaults.color = '#94a3b8';
Chart.defaults.scale.grid.color = 'rgba(148, 163, 184, 0.1)';

let priceHistoryChart = null;
let storeComparisonChart = null;

document.addEventListener('DOMContentLoaded', () => {
    initializeCharts();
    loadAnalyticsData();

    // Attach filter listeners
    const periodSelect = document.getElementById('periodSelect');
    if (periodSelect) {
        periodSelect.addEventListener('change', () => {
            loadAnalyticsData(periodSelect.value);
        });
    }
});

/**
 * Initialize empty chart instances
 */
function initializeCharts() {
    // 1. Price History Chart (Line)
    const historyCtx = document.getElementById('priceHistoryChart').getContext('2d');
    priceHistoryChart = new Chart(historyCtx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Preço Médio (R$)',
                data: [],
                borderColor: '#3b82f6',
                backgroundColor: 'rgba(59, 130, 246, 0.1)',
                borderWidth: 2,
                tension: 0.4,
                fill: true
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        label: (context) => formatCurrency(context.raw)
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: false,
                    ticks: {
                        callback: (value) => 'R$ ' + value
                    }
                }
            }
        }
    });

    // 2. Store Comparison Chart (Bar)
    const comparisonCtx = document.getElementById('storeComparisonChart').getContext('2d');
    storeComparisonChart = new Chart(comparisonCtx, {
        type: 'bar',
        data: {
            labels: [],
            datasets: [
                {
                    label: 'Produtos',
                    data: [],
                    backgroundColor: '#10b981',
                    yAxisID: 'y'
                },
                {
                    label: 'Preço Médio',
                    data: [],
                    backgroundColor: '#6366f1',
                    yAxisID: 'y1'
                }
            ]
        },
        options: {
            responsive: true,
            interaction: {
                mode: 'index',
                intersect: false,
            },
            scales: {
                y: {
                    type: 'linear',
                    display: true,
                    position: 'left',
                    title: { display: true, text: 'Quantidade' }
                },
                y1: {
                    type: 'linear',
                    display: true,
                    position: 'right',
                    title: { display: true, text: 'Preço Médio (R$)' },
                    grid: { drawOnChartArea: false },
                    ticks: {
                        callback: (value) => 'R$ ' + value
                    }
                }
            }
        }
    });
}

/**
 * Fetch and render data
 */
async function loadAnalyticsData(days = 30) {
    try {
        const [historyData, comparisonData] = await Promise.all([
            api.getAnalyticsHistory(days),
            api.getAnalyticsComparison()
        ]);

        updatePriceHistoryChart(historyData);
        updateStoreComparisonChart(comparisonData);

    } catch (error) {
        console.error('Failed to load analytics:', error);
        showToast('Erro ao carregar dados analíticos', 'error');
    }
}

function updatePriceHistoryChart(data) {
    if (!priceHistoryChart) return;

    priceHistoryChart.data.labels = data.map(item => formatDate(item.date));
    priceHistoryChart.data.datasets[0].data = data.map(item => item.average_price);
    priceHistoryChart.update();
}

function updateStoreComparisonChart(data) {
    if (!storeComparisonChart) return;

    storeComparisonChart.data.labels = data.map(item => item.store);
    storeComparisonChart.data.datasets[0].data = data.map(item => item.product_count);
    storeComparisonChart.data.datasets[1].data = data.map(item => item.average_price);
    storeComparisonChart.update();
}

/**
 * Utility: Format currency
 */
function formatCurrency(value) {
    return new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL'
    }).format(value);
}

/**
 * Utility: Format short date (DD/MM)
 */
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit' });
}
