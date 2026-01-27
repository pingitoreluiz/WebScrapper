/**
 * API Client
 * 
 * Handles all API communication with the backend
 */

const API_BASE_URL = 'http://localhost:8000';
const API_KEY = ''; // Optional: Add your API key here

class APIClient {
    constructor(baseURL = API_BASE_URL) {
        this.baseURL = baseURL;
        this.headers = {
            'Content-Type': 'application/json',
        };
        
        if (API_KEY) {
            this.headers['X-API-Key'] = API_KEY;
        }
    }

    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const config = {
            ...options,
            headers: {
                ...this.headers,
                ...options.headers,
            },
        };

        try {
            const response = await fetch(url, config);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('API request failed:', error);
            throw error;
        }
    }

    // Health
    async getHealth() {
        return this.request('/health');
    }

    async getDetailedHealth() {
        return this.request('/health/detailed');
    }

    // Products
    async getProducts(params = {}) {
        const queryString = new URLSearchParams(params).toString();
        return this.request(`/api/v1/products?${queryString}`);
    }

    async searchProducts(params = {}) {
        const queryString = new URLSearchParams(params).toString();
        return this.request(`/api/v1/products/search?${queryString}`);
    }

    async getBestDeals(limit = 10, chipBrand = null) {
        const params = { limit };
        if (chipBrand) params.chip_brand = chipBrand;
        const queryString = new URLSearchParams(params).toString();
        return this.request(`/api/v1/products/best-deals?${queryString}`);
    }

    async getProduct(id) {
        return this.request(`/api/v1/products/${id}`);
    }

    async getStats() {
        return this.request('/api/v1/products/stats/overview');
    }

    // Scrapers
    async runScrapers(stores, headless = true, maxPages = 10) {
        return this.request('/api/v1/scrapers/run', {
            method: 'POST',
            body: JSON.stringify({
                stores,
                headless,
                max_pages: maxPages,
            }),
        });
    }

    async getScraperStatus() {
        return this.request('/api/v1/scrapers/status');
    }

    async getScraperHistory(limit = 10) {
        return this.request(`/api/v1/scrapers/history?limit=${limit}`);
    }

    async getScraperMetrics(days = 7) {
        return this.request(`/api/v1/scrapers/metrics?days=${days}`);
    }
}

// Create global API instance
const api = new APIClient();

// Utility functions
function formatCurrency(value) {
    return new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL',
    }).format(value);
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return new Intl.DateTimeFormat('pt-BR', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
    }).format(date);
}

function formatRelativeTime(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'Agora mesmo';
    if (diffMins < 60) return `Há ${diffMins} minuto${diffMins > 1 ? 's' : ''}`;
    if (diffHours < 24) return `Há ${diffHours} hora${diffHours > 1 ? 's' : ''}`;
    return `Há ${diffDays} dia${diffDays > 1 ? 's' : ''}`;
}

function showToast(message, type = 'success') {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.className = `toast show toast-${type}`;
    
    setTimeout(() => {
        toast.className = 'toast';
    }, 3000);
}

function showLoading(element) {
    element.innerHTML = '<div class="loading">Carregando...</div>';
}

function showError(element, message = 'Erro ao carregar dados') {
    element.innerHTML = `<div class="error">${message}</div>`;
}
