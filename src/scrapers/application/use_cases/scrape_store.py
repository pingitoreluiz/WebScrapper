"""
ScrapeStore use case - Main orchestration for scraping a store.

This use case coordinates browser, extractor, and repository to scrape products.
"""

from datetime import datetime
from typing import List

from ...domain.entities.product import Product
from ...domain.entities.scraper_run import ScraperRun
from ...domain.value_objects.price import Price
from ...domain.value_objects.url import ProductUrl
from ...domain.repositories.product_repository import ProductRepository
from ...domain.repositories.scraper_run_repository import ScraperRunRepository
from ..dtos.scraper_config import ScraperConfigDTO
from ..dtos.scraper_metrics import ScraperMetricsDTO
from ..dtos.extraction_result import ExtractionResultDTO
from ..interfaces.browser_service import BrowserService
from ..interfaces.extractor_service import ExtractorService


class ScrapeStoreUseCase:
    """
    Use case for scraping a store.
    
    This orchestrates the entire scraping process:
    1. Initialize browser
    2. Navigate through pages
    3. Extract product data
    4. Create domain entities
    5. Save to repository
    6. Track metrics
    
    Attributes:
        browser_service: Service for browser operations
        extractor_service: Service for data extraction
        product_repository: Repository for product persistence
        scraper_run_repository: Repository for run metrics
    """
    
    def __init__(
        self,
        browser_service: BrowserService,
        extractor_service: ExtractorService,
        product_repository: ProductRepository,
        scraper_run_repository: ScraperRunRepository,
    ):
        """
        Initialize use case with dependencies.
        
        Args:
            browser_service: Browser service implementation
            extractor_service: Extractor service implementation
            product_repository: Product repository implementation
            scraper_run_repository: Scraper run repository implementation
        """
        self.browser = browser_service
        self.extractor = extractor_service
        self.product_repo = product_repository
        self.run_repo = scraper_run_repository
    
    async def execute(self, config: ScraperConfigDTO) -> ScraperMetricsDTO:
        """
        Execute the scraping use case.
        
        Args:
            config: Scraper configuration DTO
            
        Returns:
            Metrics DTO with execution results
        """
        # Validate configuration
        config.validate()
        
        # Create scraper run entity
        run = ScraperRun(store=config.store)
        run.start()
        
        try:
            # Initialize browser
            await self.browser.initialize(
                headless=config.headless,
                user_agent=config.user_agent,
                viewport=config.viewport,
                timeout=config.timeout,
            )
            
            # Scrape pages
            page_num = 1
            while page_num <= config.max_pages:
                # Build URL for page
                url = self.extractor.build_url(page_num)
                
                # Navigate to page
                await self.browser.navigate(url, timeout=config.timeout)
                
                # Get page content
                page_content = await self.browser.get_page_content()
                
                # Extract products
                extraction_results = await self.extractor.extract_products(
                    page_content
                )
                
                # Process each extracted product
                for result in extraction_results:
                    run.increment_products_found()
                    
                    if result.is_valid():
                        product = self._create_product_from_dto(result, config.store)
                        saved_product = self.product_repo.save(product)
                        run.add_product(saved_product)
                        run.increment_products_saved()
                    else:
                        run.increment_products_skipped()
                
                run.increment_pages_scraped()
                
                # Check if should continue
                if not self.extractor.should_continue(
                    page_num, run.products_found
                ):
                    break
                
                page_num += 1
            
            # Mark as successful
            run.finish_successfully()
            
        except Exception as e:
            # Mark as failed
            run.finish_with_error(str(e))
            run.increment_errors()
            
        finally:
            # Cleanup browser
            await self.browser.close()
            
            # Save run metrics
            self.run_repo.save(run)
        
        # Convert to DTO and return
        return self._create_metrics_dto(run)
    
    def _create_product_from_dto(
        self, dto: ExtractionResultDTO, store: str
    ) -> Product:
        """
        Create Product entity from extraction DTO.
        
        Args:
            dto: Extraction result DTO
            store: Store name
            
        Returns:
            Product domain entity
        """
        # Create value objects
        price = Price.from_string(dto.price_raw)
        url = ProductUrl(dto.url)
        
        # Create product entity
        product = Product(
            title=dto.title,
            price=price,
            url=url,
            store=store,
            available=dto.available,
            chip_brand=dto.extra_data.get("chip_brand"),
            manufacturer=dto.extra_data.get("manufacturer"),
            model=dto.extra_data.get("model"),
        )
        
        return product
    
    def _create_metrics_dto(self, run: ScraperRun) -> ScraperMetricsDTO:
        """
        Create metrics DTO from scraper run entity.
        
        Args:
            run: ScraperRun entity
            
        Returns:
            ScraperMetrics DTO
        """
        return ScraperMetricsDTO(
            store=run.store,
            started_at=run.started_at,
            finished_at=run.finished_at,
            execution_time=run.execution_time,
            products_found=run.products_found,
            products_saved=run.products_saved,
            products_skipped=run.products_skipped,
            pages_scraped=run.pages_scraped,
            errors=run.errors,
            captchas_detected=run.captchas_detected,
            success=run.success,
            error_message=run.error_message,
        )
