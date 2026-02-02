"""
Integration tests for API with database

Tests API endpoints with real database interactions
"""

import pytest
from fastapi.testclient import TestClient
from src.backend.api.app import create_app
from src.backend.core.models import Store
from src.backend.core.database_models import Product


@pytest.fixture
def client(db_session):
    """Create test client with database"""
    app = create_app()

    # Override database dependency
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    from src.backend.core.database import get_db

    app.dependency_overrides[get_db] = override_get_db

    return TestClient(app)


class TestProductEndpoints:
    """Test product API endpoints with database"""

    def test_list_products_with_data(self, client, sample_products):
        """Test listing products from database"""
        response = client.get("/api/v1/products")

        assert response.status_code == 200
        data = response.json()

        assert isinstance(data, list)
        assert len(data) == 3

    def test_search_products(self, client, sample_products):
        """Test product search with database"""
        response = client.get("/api/v1/products/search?query=RTX")

        assert response.status_code == 200
        data = response.json()

        assert isinstance(data, list)
        assert len(data) >= 2  # Should find RTX 4090 and 4080
        assert all("RTX" in item["title"] for item in data)

    def test_filter_by_chip_brand(self, client, sample_products):
        """Test filtering by chip brand"""
        response = client.get("/api/v1/products?chip_brand=NVIDIA")

        assert response.status_code == 200
        data = response.json()

        assert isinstance(data, list)
        assert all(item["chip_brand"] == "NVIDIA" for item in data)

    def test_filter_by_store(self, client, sample_products):
        """Test filtering by store"""
        response = client.get("/api/v1/products?store=Pichau")

        assert response.status_code == 200
        data = response.json()

        assert isinstance(data, list)
        assert all(item["store"] == "Pichau" for item in data)

    def test_price_range_filter(self, client, sample_products):
        """Test filtering by price range"""
        response = client.get("/api/v1/products?min_price=7000&max_price=9000")

        assert response.status_code == 200
        data = response.json()

        assert isinstance(data, list)
        for item in data:
            assert 7000 <= item["price"] <= 9000

    def test_pagination(self, client, sample_products):
        """Test pagination"""
        # Get first page
        response1 = client.get("/api/v1/products?limit=2&offset=0")
        assert response1.status_code == 200
        data1 = response1.json()
        assert len(data1) == 2

        # Get second page
        response2 = client.get("/api/v1/products?limit=2&offset=2")
        assert response2.status_code == 200
        data2 = response2.json()
        assert len(data2) == 1

    def test_get_product_by_id(self, client, sample_products):
        """Test getting single product"""
        product_id = sample_products[0].id
        response = client.get(f"/api/v1/products/{product_id}")

        assert response.status_code == 200
        data = response.json()

        assert data["id"] == product_id
        assert data["title"] == sample_products[0].title

    def test_get_nonexistent_product(self, client):
        """Test getting product that doesn't exist"""
        response = client.get("/api/v1/products/99999")

        assert response.status_code == 404

    def test_best_deals(self, client, sample_products):
        """Test best deals endpoint"""
        response = client.get("/api/v1/products/best-deals?limit=2")

        assert response.status_code == 200
        data = response.json()

        assert isinstance(data, list)
        assert len(data) <= 2
        # Should be sorted by price (ascending)
        if len(data) > 1:
            assert data[0]["price"] <= data[1]["price"]

    def test_stats_endpoint(self, client, sample_products):
        """Test statistics endpoint"""
        response = client.get("/api/v1/products/stats/overview")

        assert response.status_code == 200
        data = response.json()

        assert "total_products" in data
        assert "avg_price" in data
        assert "by_store" in data
        assert data["total_products"] == 3


class TestScraperEndpoints:
    """Test scraper API endpoints"""

    def test_scraper_history(self, client, sample_scraper_run):
        """Test getting scraper history"""
        response = client.get("/api/v1/scrapers/history?limit=10")

        assert response.status_code == 200
        data = response.json()

        assert isinstance(data, dict)
        assert "total" in data
        assert "runs" in data
        assert len(data["runs"]) > 0
        assert data["runs"][0]["store"] == "Pichau"

    def test_scraper_metrics(self, client, sample_scraper_run):
        """Test getting scraper metrics"""
        response = client.get("/api/v1/scrapers/metrics?days=7")

        assert response.status_code == 200
        data = response.json()

        assert "total_runs" in data
        assert "success_rate" in data


class TestAPIValidation:
    """Test API input validation"""

    def test_invalid_limit(self, client):
        """Test invalid limit parameter"""
        response = client.get("/api/v1/products?limit=-1")

        assert response.status_code == 422  # Validation error

    def test_invalid_price_range(self, client):
        """Test invalid price range"""
        response = client.get("/api/v1/products?min_price=10000&max_price=1000")

        # Should handle gracefully (return empty or error)
        assert response.status_code in [200, 400]

    def test_invalid_chip_brand(self, client):
        """Test invalid chip brand"""
        response = client.get("/api/v1/products?chip_brand=INVALID")

        # Validation error
        assert response.status_code == 422
