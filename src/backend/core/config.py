"""
Application configuration using Pydantic Settings

Loads configuration from environment variables with validation.
"""

from typing import List, Optional
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseConfig(BaseSettings):
    """Database configuration"""

    url: str = Field(default="sqlite:///data/prices.db", description="Database URL")
    echo: bool = Field(default=False, description="Echo SQL queries")
    pool_size: int = Field(default=5, description="Connection pool size")
    max_overflow: int = Field(default=10, description="Max overflow connections")

    model_config = SettingsConfigDict(env_prefix="DB_", extra="ignore")


class APIConfig(BaseSettings):
    """API server configuration"""

    host: str = Field(default="0.0.0.0", description="API host")
    port: int = Field(default=8000, description="API port")
    workers: int = Field(default=4, description="Number of workers")
    api_key: str = Field(
        default="change-this-secret-key", description="API authentication key"
    )
    cors_origins: List[str] = Field(default=["*"], description="CORS allowed origins")

    model_config = SettingsConfigDict(env_prefix="API_", extra="ignore")


class ScraperConfig(BaseSettings):
    """Scraper configuration"""

    max_concurrent: int = Field(default=3, description="Max concurrent scrapers")
    timeout: int = Field(default=60, description="Scraper timeout in seconds")
    headless: bool = Field(default=True, description="Run browser in headless mode")
    max_pages: int = Field(default=20, description="Max pages per scraper")

    # Timing configuration
    min_delay: float = Field(
        default=1.5, description="Min delay between actions (seconds)"
    )
    max_delay: float = Field(
        default=3.5, description="Max delay between actions (seconds)"
    )
    page_timeout: int = Field(default=30000, description="Page load timeout (ms)")
    selector_timeout: int = Field(
        default=15000, description="Selector wait timeout (ms)"
    )

    # Anti-detection
    user_agent_rotation: bool = Field(default=True, description="Rotate user agents")
    random_delays: bool = Field(default=True, description="Use random delays")

    # Validation
    min_price: float = Field(default=100.0, description="Minimum valid price")
    max_price: float = Field(default=50000.0, description="Maximum valid price")

    # Keywords
    unavailable_keywords: List[str] = Field(
        default=["indisponível", "esgotado", "avise-me", "out of stock"],
        description="Keywords indicating product unavailability",
    )

    model_config = SettingsConfigDict(env_prefix="SCRAPER_", extra="ignore")

    @field_validator("max_concurrent")
    @classmethod
    def validate_max_concurrent(cls, v: int) -> int:
        if v < 1 or v > 10:
            raise ValueError("max_concurrent must be between 1 and 10")
        return v


class RedisConfig(BaseSettings):
    """Redis configuration"""

    host: str = Field(default="localhost", description="Redis host")
    port: int = Field(default=6379, description="Redis port")
    db: int = Field(default=0, description="Redis database number")
    password: Optional[str] = Field(default=None, description="Redis password")

    model_config = SettingsConfigDict(env_prefix="REDIS_", extra="ignore")


class MonitoringConfig(BaseSettings):
    """Monitoring configuration"""

    prometheus_port: int = Field(default=9090, description="Prometheus port")
    grafana_port: int = Field(default=3000, description="Grafana port")
    enable_metrics: bool = Field(default=True, description="Enable metrics collection")

    model_config = SettingsConfigDict(env_prefix="MONITORING_", extra="ignore")


class AppConfig(BaseSettings):
    """Main application configuration"""

    env: str = Field(
        default="development", description="Environment (development/production)"
    )
    debug: bool = Field(default=True, description="Debug mode")
    log_level: str = Field(default="INFO", description="Logging level")

    # Sub-configurations
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    api: APIConfig = Field(default_factory=APIConfig)
    scraper: ScraperConfig = Field(default_factory=ScraperConfig)
    redis: RedisConfig = Field(default_factory=RedisConfig)
    monitoring: MonitoringConfig = Field(default_factory=MonitoringConfig)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        env_prefix="APP_",
        extra="ignore",
    )

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        v_upper = v.upper()
        if v_upper not in valid_levels:
            raise ValueError(f"log_level must be one of {valid_levels}")
        return v_upper


# Global configuration instance
_config: Optional[AppConfig] = None


def get_config() -> AppConfig:
    """
    Get the global configuration instance (singleton pattern)

    Returns:
        AppConfig instance
    """
    global _config
    if _config is None:
        _config = AppConfig()
    return _config


def reload_config() -> AppConfig:
    """
    Reload configuration from environment

    Returns:
        New AppConfig instance
    """
    global _config
    _config = AppConfig()
    return _config


# Store URLs configuration
STORE_URLS = {
    "pichau": "https://www.pichau.com.br/hardware/placa-de-video",
    "kabum": "https://www.kabum.com.br/hardware/placa-de-video-vga",
    "terabyte": "https://www.terabyteshop.com.br/hardware/placas-de-video",
}

# Known GPU manufacturers
KNOWN_MANUFACTURERS = [
    "ASUS",
    "MSI",
    "GIGABYTE",
    "GALAX",
    "XFX",
    "ASROCK",
    "ZOTAC",
    "PNY",
    "POWERCOLOR",
    "SAPPHIRE",
    "COLORFUL",
    "INNO3D",
    "PALIT",
    "EVGA",
    "PCYES",
    "MANCER",
    "GAINWARD",
    "AFOX",
    "BIOSTAR",
    "MANLI",
    "MAXSUN",
    "LEADTEK",
    "SPARKLE",
    "SUPERFRAME",
    "DUEX",
]

# User agents for rotation
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
]

# Browser viewports
VIEWPORTS = [
    {"width": 1920, "height": 1080},
    {"width": 1366, "height": 768},
    {"width": 1536, "height": 864},
    {"width": 1440, "height": 900},
    {"width": 1280, "height": 720},
]

# Brazilian timezones with coordinates
TIMEZONES = [
    ("America/Sao_Paulo", -23.5505, -46.6333, "São Paulo"),
    ("America/Sao_Paulo", -22.9068, -43.1729, "Rio de Janeiro"),
    ("America/Fortaleza", -3.7172, -38.5433, "Fortaleza"),
    ("America/Manaus", -3.1190, -60.0217, "Manaus"),
]
