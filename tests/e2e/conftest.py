"""
E2E test configuration for Playwright

Provides browser fixtures and setup for end-to-end testing
"""

import pytest
from playwright.sync_api import sync_playwright, Browser, Page, BrowserContext


@pytest.fixture(scope="session")
def browser():
    """Create browser instance for all E2E tests"""
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=['--disable-dev-shm-usage']
        )
        yield browser
        browser.close()


@pytest.fixture(scope="function")
def context(browser: Browser) -> BrowserContext:
    """Create new browser context for each test"""
    context = browser.new_context(
        viewport={'width': 1920, 'height': 1080},
        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    )
    yield context
    context.close()


@pytest.fixture(scope="function")
def page(context: BrowserContext) -> Page:
    """Create new page for each test"""
    page = context.new_page()
    yield page
    page.close()


@pytest.fixture
def base_url():
    """Base URL for the application"""
    return "http://localhost"


@pytest.fixture
def api_base_url():
    """Base URL for the API"""
    return "http://localhost:8000"
