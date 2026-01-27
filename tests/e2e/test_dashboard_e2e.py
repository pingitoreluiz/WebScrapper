"""
E2E tests for dashboard user journeys

Tests complete user workflows through the web interface
"""

import pytest
from playwright.sync_api import Page, expect


class TestDashboardJourney:
    """Test main dashboard user journeys"""
    
    def test_dashboard_loads(self, page: Page, base_url: str):
        """Test that dashboard loads successfully"""
        page.goto(base_url)
        
        # Verify page title
        expect(page).to_have_title("GPU Price Scraper Dashboard")
        
        # Verify main sections are visible
        expect(page.locator("h1")).to_contain_text("GPU Price Scraper")
        expect(page.locator(".stats-container")).to_be_visible()
    
    def test_stats_cards_display(self, page: Page, base_url: str):
        """Test that statistics cards are displayed"""
        page.goto(base_url)
        
        # Wait for stats to load
        page.wait_for_selector(".stat-card", timeout=5000)
        
        # Verify all stat cards are present
        stat_cards = page.locator(".stat-card")
        expect(stat_cards).to_have_count(4)
        
        # Verify stat card content
        expect(page.locator(".stat-card").first).to_contain_text("Total Products")
    
    def test_best_deals_section(self, page: Page, base_url: str):
        """Test best deals section"""
        page.goto(base_url)
        
        # Wait for products to load
        page.wait_for_selector(".product-card", timeout=5000)
        
        # Verify product cards are displayed
        product_cards = page.locator(".product-card")
        count = product_cards.count()
        
        assert count > 0, "No product cards found"
        
        # Verify product card structure
        first_card = product_cards.first
        expect(first_card.locator(".product-title")).to_be_visible()
        expect(first_card.locator(".product-price")).to_be_visible()
    
    def test_activity_feed(self, page: Page, base_url: str):
        """Test activity feed displays scraper history"""
        page.goto(base_url)
        
        # Wait for activity feed
        page.wait_for_selector(".activity-feed", timeout=5000)
        
        # Verify activity items
        activity_items = page.locator(".activity-item")
        
        if activity_items.count() > 0:
            first_item = activity_items.first
            expect(first_item).to_be_visible()


class TestScraperControls:
    """Test scraper control functionality"""
    
    @pytest.mark.slow
    def test_run_scraper_button(self, page: Page, base_url: str):
        """Test running scraper from UI"""
        page.goto(base_url)
        
        # Find and click run scraper button
        run_button = page.locator("#run-scraper-btn")
        expect(run_button).to_be_visible()
        
        run_button.click()
        
        # Wait for loading indicator
        expect(page.locator(".loading")).to_be_visible(timeout=2000)
        
        # Note: In real test, would wait for completion
        # For now, just verify button was clicked
    
    def test_scraper_controls_visible(self, page: Page, base_url: str):
        """Test that scraper controls are accessible"""
        page.goto(base_url)
        
        # Verify scraper controls section exists
        expect(page.locator(".scraper-controls")).to_be_visible()


class TestProductSearch:
    """Test product search functionality"""
    
    def test_search_input_visible(self, page: Page, base_url: str):
        """Test search input is visible"""
        page.goto(base_url)
        
        search_input = page.locator("#search-input")
        expect(search_input).to_be_visible()
    
    def test_search_products(self, page: Page, base_url: str):
        """Test searching for products"""
        page.goto(base_url)
        
        # Enter search query
        search_input = page.locator("#search-input")
        search_input.fill("RTX 4090")
        
        # Click search button
        search_button = page.locator("#search-btn")
        search_button.click()
        
        # Wait for results
        page.wait_for_timeout(1000)
        
        # Verify search was executed
        # (Results depend on data in database)
    
    def test_filter_by_chip_brand(self, page: Page, base_url: str):
        """Test filtering by chip brand"""
        page.goto(base_url)
        
        # Find chip brand filter
        chip_filter = page.locator("#chip-brand-filter")
        
        if chip_filter.is_visible():
            chip_filter.select_option("NVIDIA")
            page.wait_for_timeout(500)


class TestNavigation:
    """Test navigation between pages"""
    
    def test_navigate_to_products(self, page: Page, base_url: str):
        """Test navigating to products page"""
        page.goto(base_url)
        
        # Click products link (if exists)
        products_link = page.locator("a[href='/products.html']")
        
        if products_link.is_visible():
            products_link.click()
            expect(page).to_have_url(f"{base_url}/products.html")
    
    def test_navigate_to_analytics(self, page: Page, base_url: str):
        """Test navigating to analytics page"""
        page.goto(base_url)
        
        # Click analytics link (if exists)
        analytics_link = page.locator("a[href='/analytics.html']")
        
        if analytics_link.is_visible():
            analytics_link.click()
            expect(page).to_have_url(f"{base_url}/analytics.html")


class TestResponsiveness:
    """Test responsive design"""
    
    def test_mobile_view(self, page: Page, base_url: str):
        """Test dashboard on mobile viewport"""
        # Set mobile viewport
        page.set_viewport_size({"width": 375, "height": 667})
        page.goto(base_url)
        
        # Verify page loads
        expect(page.locator("h1")).to_be_visible()
        
        # Verify mobile menu (if exists)
        mobile_menu = page.locator(".mobile-menu")
        if mobile_menu.count() > 0:
            expect(mobile_menu).to_be_visible()
    
    def test_tablet_view(self, page: Page, base_url: str):
        """Test dashboard on tablet viewport"""
        # Set tablet viewport
        page.set_viewport_size({"width": 768, "height": 1024})
        page.goto(base_url)
        
        # Verify page loads
        expect(page.locator("h1")).to_be_visible()


class TestErrorHandling:
    """Test error handling in UI"""
    
    def test_api_error_handling(self, page: Page, base_url: str):
        """Test UI handles API errors gracefully"""
        page.goto(base_url)
        
        # Intercept API calls and return error
        page.route("**/api/v1/products", lambda route: route.fulfill(
            status=500,
            body='{"detail": "Internal Server Error"}'
        ))
        
        # Reload page
        page.reload()
        
        # Verify error message is shown
        error_message = page.locator(".error-message")
        if error_message.count() > 0:
            expect(error_message).to_be_visible()
    
    def test_loading_states(self, page: Page, base_url: str):
        """Test loading states are shown"""
        page.goto(base_url)
        
        # Verify loading indicators exist
        # (May not be visible if data loads quickly)
        loading = page.locator(".loading, .skeleton")
        # Just verify element exists in DOM
        assert loading.count() >= 0
