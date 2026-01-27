"""
FastAPI application core

Main application setup with middleware, exception handlers, and configuration.
"""

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager

from ..core.config import get_config
from ..core.database import create_tables
from ...utils.logger import get_logger, configure_logging

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager
    
    Handles startup and shutdown events.
    """
    # Startup
    logger.info("application_starting")
    
    # Configure logging
    config = get_config()
    configure_logging(
        log_level=config.log_level,
        json_logs=(config.env == "production")
    )
    
    # Create database tables
    create_tables()
    
    logger.info("application_started", env=config.env)
    
    yield
    
    # Shutdown
    logger.info("application_shutting_down")


def create_app() -> FastAPI:
    """
    Create and configure FastAPI application
    
    Returns:
        Configured FastAPI instance
    """
    config = get_config()
    
    app = FastAPI(
        title="WebScraper API",
        description="API for GPU price scraping and analytics",
        version="2.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.api.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Register exception handlers
    register_exception_handlers(app)
    
    # Register routes
    register_routes(app)
    
    logger.info("fastapi_app_created")
    
    return app


def register_exception_handlers(app: FastAPI) -> None:
    """Register custom exception handlers"""
    
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """Handle validation errors"""
        logger.warning(
            "validation_error",
            path=request.url.path,
            errors=exc.errors()
        )
        
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": "Validation Error",
                "detail": exc.errors(),
                "path": str(request.url.path)
            }
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """Handle unexpected errors"""
        logger.error(
            "unexpected_error",
            path=request.url.path,
            error=str(exc),
            exc_info=True
        )
        
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "Internal Server Error",
                "message": "An unexpected error occurred",
                "path": str(request.url.path)
            }
        )


def register_routes(app: FastAPI) -> None:
    """Register API routes"""
    from .routes import health, products, scrapers, analytics
    
    # Health check (no prefix)
    app.include_router(health.router, tags=["Health"])
    
    # API v1 routes
    app.include_router(
        products.router,
        prefix="/api/v1/products",
        tags=["Products"]
    )
    
    app.include_router(
        scrapers.router,
        prefix="/api/v1/scrapers",
        tags=["Scrapers"]
    )

    app.include_router(
        analytics.router,
        prefix="/api/v1/analytics",
        tags=["Analytics"]
    )
    
    logger.info("routes_registered")


# Create app instance
app = create_app()
