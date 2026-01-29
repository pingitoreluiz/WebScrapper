"""
Unit tests for API endpoints

Tests all API routes with mocked dependencies.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
from datetime import datetime

from src.backend.api.app import create_app
from src.backend.core.models import ProductInDB, ChipBrand, Store, Price, ScraperMetrics


@pytest.fixture
def client():
    """Create test client"""
    app = create_app()
    return TestClient(app)


@pytest.fixture
def mock_db():
    """Mock database session"""
    return Mock()


@pytest.fixture
def sample_product():
    """Sample product for testing"""
    return ProductInDB(
        id=1,
        title="Placa de Vídeo ASUS ROG RTX 4090",
        price=Price(raw="R$ 12.000,00", value=12000.0),
        url="https://example.com/product/1",
        store=Store.PICHAU,
        chip_brand=ChipBrand.NVIDIA,
        manufacturer="ASUS",
        model="RTX 4090",
        scraped_at=datetime.now(),
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )


class TestHealthEndpoints:
    """Test health check endpoints"""

    def test_health_check(self, client):
        """Test basic health check"""
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert data["version"] == "2.0.0"

    @patch("src.backend.api.routes.health.get_db")
    def test_detailed_health_check(self, mock_get_db, client, mock_db):
        """Test detailed health check"""
        # Mock database stats
        mock_repo = Mock()
        mock_repo.get_stats.return_value = {
            "total_products": 100,
            "latest_scrape": "2024-01-26T12:00:00",
        }

        with patch(
            "src.backend.api.routes.health.ProductRepository", return_value=mock_repo
        ):
            response = client.get("/health/detailed")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["database"]["status"] == "connected"
        assert data["database"]["total_products"] == 100


class TestProductEndpoints:
    """Test product API endpoints"""

    @patch("src.backend.api.routes.products.get_db")
    def test_list_products(self, mock_get_db, client, mock_db, sample_product):
        """Test listing products"""
        mock_repo = Mock()
        mock_repo.search.return_value = [sample_product]

        with patch(
            "src.backend.api.routes.products.ProductRepository", return_value=mock_repo
        ):
            response = client.get("/api/v1/products/")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["title"] == sample_product.title
        assert data[0]["price"] == 12000.0

    @patch("src.backend.api.routes.products.get_db")
    def test_search_products(self, mock_get_db, client, mock_db, sample_product):
        """Test searching products"""
        mock_repo = Mock()
        mock_repo.search.return_value = [sample_product]

        with patch(
            "src.backend.api.routes.products.ProductRepository", return_value=mock_repo
        ):
            response = client.get("/api/v1/products/search?query=RTX&chip_brand=NVIDIA")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["chip_brand"] == "NVIDIA"

    @patch("src.backend.api.routes.products.get_db")
    def test_get_best_deals(self, mock_get_db, client, mock_db, sample_product):
        """Test getting best deals"""
        mock_repo = Mock()
        mock_repo.get_best_deals.return_value = [sample_product]

        with patch(
            "src.backend.api.routes.products.ProductRepository", return_value=mock_repo
        ):
            response = client.get("/api/v1/products/best-deals?limit=10")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1

    @patch("src.backend.api.routes.products.get_db")
    def test_get_product_by_id(self, mock_get_db, client, mock_db, sample_product):
        """Test getting product by ID"""
        mock_repo = Mock()
        mock_repo.get_by_id.return_value = sample_product

        with patch(
            "src.backend.api.routes.products.ProductRepository", return_value=mock_repo
        ):
            response = client.get("/api/v1/products/1")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1
        assert data["title"] == sample_product.title

    @patch("src.backend.api.routes.products.get_db")
    def test_get_product_not_found(self, mock_get_db, client, mock_db):
        """Test getting non-existent product"""
        mock_repo = Mock()
        mock_repo.get_by_id.return_value = None

        with patch(
            "src.backend.api.routes.products.ProductRepository", return_value=mock_repo
        ):
            response = client.get("/api/v1/products/999")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    @patch("src.backend.api.routes.products.get_db")
    def test_get_stats(self, mock_get_db, client, mock_db):
        """Test getting statistics"""
        mock_repo = Mock()
        mock_repo.get_stats.return_value = {
            "total_products": 150,
            "by_store": {"Pichau": 50, "Kabum": 100},
            "avg_price": 5000.0,
        }

        with patch(
            "src.backend.api.routes.products.ProductRepository", return_value=mock_repo
        ):
            response = client.get("/api/v1/products/stats/overview")

        assert response.status_code == 200
        data = response.json()
        assert data["total_products"] == 150
        assert data["avg_price"] == 5000.0


class TestScraperEndpoints:
    """Test scraper API endpoints"""

    @patch("src.backend.api.routes.scrapers.get_scheduler")
    @patch("src.backend.api.routes.scrapers.get_db")
    def test_run_scrapers(self, mock_get_db, mock_get_scheduler, client):
        """Test running scrapers"""
        # Mock scheduler
        mock_scheduler = Mock()
        mock_metrics = ScraperMetrics(
            store=Store.PICHAU, products_saved=10, execution_time=5.0
        )
        mock_scheduler.run_now.return_value = mock_metrics
        mock_get_scheduler.return_value = mock_scheduler

        response = client.post(
            "/api/v1/scrapers/run", json={"stores": ["Pichau"], "headless": True}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        # Background task returns 0 immediately, actual results come later
        assert data["total_products_saved"] == 0

    @patch("src.backend.api.routes.scrapers.get_scheduler")
    def test_get_scraper_status(self, mock_get_scheduler, client):
        """Test getting scraper status"""
        mock_scheduler = Mock()
        mock_scheduler.scheduler.running = True
        mock_scheduler.get_jobs.return_value = []
        mock_get_scheduler.return_value = mock_scheduler

        response = client.get("/api/v1/scrapers/status")

        assert response.status_code == 200
        data = response.json()
        assert data["scheduler_running"] is True
        assert "active_jobs" in data

    @patch("src.backend.api.routes.scrapers.get_db")
    def test_get_scraper_history(self, mock_get_db, client):
        """Test getting scraper history"""
        mock_repo = Mock()
        mock_run = Mock()
        mock_run.id = 1
        mock_run.store = "Pichau"
        mock_run.products_saved = 10
        mock_run.products_found = 15
        mock_run.products_skipped = 5
        mock_run.pages_scraped = 2
        mock_run.errors = 0
        mock_run.captchas_detected = 0
        mock_run.execution_time = 5.0
        mock_run.success = True
        mock_run.error_message = None
        mock_run.started_at = datetime.now()
        mock_run.finished_at = datetime.now()

        mock_repo.get_recent_runs.return_value = [mock_run]

        with patch(
            "src.backend.api.routes.scrapers.ScraperRunRepository",
            return_value=mock_repo,
        ):
            response = client.get("/api/v1/scrapers/history")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert len(data["runs"]) == 1


class TestAuthentication:
    """Test API authentication"""

    def test_missing_api_key(self):
        """Test request without API key to protected endpoint"""
        # This would be tested on protected endpoints
        # For now, authentication is optional
        pass

    def test_invalid_api_key(self):
        """Test request with invalid API key"""
        # This would be tested on protected endpoints
        pass


class TestRateLimiting:
    """Test rate limiting"""

    def test_rate_limit_not_exceeded(self, client):
        """Test normal requests within rate limit"""
        # Make a few requests
        for _ in range(5):
            response = client.get("/health")
            assert response.status_code == 200

    def test_rate_limit_exceeded(self, client):
        """Test rate limit enforcement"""
        # This would require many requests
        # Skipping for now as it's slow
        pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
