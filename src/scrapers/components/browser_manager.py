"""
Browser lifecycle management with anti-detection features

Manages Playwright browser instances with stealth configuration.
"""

import random
from typing import Optional, Dict, Tuple
from contextlib import contextmanager

from playwright.sync_api import sync_playwright, Browser, BrowserContext, Page, Playwright

from ..models import BrowserConfig
from ...backend.core.config import USER_AGENTS, VIEWPORTS, TIMEZONES
from ...utils.logger import get_logger

logger = get_logger(__name__)


class BrowserManager:
    """
    Manages browser lifecycle with anti-detection
    
    Features:
    - Random user agents and viewports
    - Brazilian timezone and geolocation
    - Stealth scripts to hide automation
    - Context manager support
    """
    
    def __init__(self, config: Optional[BrowserConfig] = None):
        self.config = config or BrowserConfig()
        self.playwright: Optional[Playwright] = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
    
    def __enter__(self) -> Page:
        """Context manager entry - setup browser"""
        return self.start()
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - cleanup browser"""
        self.stop()
        return False  # Don't suppress exceptions
    
    def start(self) -> Page:
        """
        Start browser and return page
        
        Returns:
            Playwright Page instance
        """
        logger.debug("starting_browser", headless=self.config.headless)
        
        # Start Playwright
        self.playwright = sync_playwright().start()
        
        # Launch browser
        self.browser = self._launch_browser()
        
        # Create context with anti-detection
        self.context = self._create_context()
        
        # Create page
        self.page = self.context.new_page()
        
        # Inject stealth scripts
        if self.config.remove_webdriver_flag:
            self._inject_stealth_scripts()
        
        logger.debug("browser_started")
        
        return self.page
    
    def stop(self) -> None:
        """Stop browser and cleanup resources"""
        logger.debug("stopping_browser")
        
        if self.browser:
            self.browser.close()
        
        if self.playwright:
            self.playwright.stop()
        
        logger.debug("browser_stopped")
    
    def _launch_browser(self) -> Browser:
        """Launch Chromium with anti-detection args"""
        if not self.playwright:
            raise RuntimeError("Playwright not started")
        
        args = [
            '--disable-blink-features=AutomationControlled',
            '--disable-dev-shm-usage',
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--disable-infobars',
            '--window-position=0,0',
            '--ignore-certificate-errors',
        ]
        
        return self.playwright.chromium.launch(
            headless=self.config.headless,
            args=args
        )
    
    def _create_context(self) -> BrowserContext:
        """Create browser context with randomized settings"""
        if not self.browser:
            raise RuntimeError("Browser not launched")
        
        # Select random user agent and viewport
        user_agent = self.config.user_agent or random.choice(USER_AGENTS)
        viewport = self.config.viewport or random.choice(VIEWPORTS)
        
        # Select random Brazilian timezone
        tz_id, lat, lon, city = random.choice(TIMEZONES)
        
        logger.debug(
            "creating_context",
            user_agent=user_agent[:50],
            viewport=viewport,
            timezone=tz_id,
            city=city
        )
        
        return self.browser.new_context(
            user_agent=user_agent,
            viewport=viewport,
            locale=self.config.locale,
            timezone_id=tz_id,
            permissions=['geolocation'],
            geolocation={'latitude': lat, 'longitude': lon},
            extra_http_headers={
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1',
                'Cache-Control': 'max-age=0',
            }
        )
    
    def _inject_stealth_scripts(self) -> None:
        """Inject JavaScript to hide automation"""
        if not self.page:
            return
        
        stealth_script = """
        // Remove webdriver flag
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        });
        
        // Add chrome object
        window.chrome = {
            runtime: {},
            loadTimes: function() {},
            csi: function() {},
            app: {}
        };
        
        // Add realistic plugins
        Object.defineProperty(navigator, 'plugins', {
            get: () => [1, 2, 3, 4, 5]
        });
        
        // Set languages
        Object.defineProperty(navigator, 'languages', {
            get: () => ['pt-BR', 'pt', 'en-US', 'en']
        });
        
        // Mock permissions
        const originalQuery = window.navigator.permissions.query;
        window.navigator.permissions.query = (parameters) => (
            parameters.name === 'notifications' ?
                Promise.resolve({ state: Notification.permission }) :
                originalQuery(parameters)
        );
        """
        
        self.page.add_init_script(stealth_script)
        logger.debug("stealth_scripts_injected")


@contextmanager
def get_browser(config: Optional[BrowserConfig] = None):
    """
    Context manager for browser instances
    
    Usage:
        >>> with get_browser() as page:
        ...     page.goto("https://example.com")
    """
    manager = BrowserManager(config)
    try:
        yield manager.start()
    finally:
        manager.stop()
