"""
Configurações centralizadas do projeto de scraping
"""

# URLs base das lojas
STORE_URLS = {
    "pichau": "https://www.pichau.com.br/hardware/placa-de-video",
    "kabum": "https://www.kabum.com.br/hardware/placa-de-video-vga",
    "terabyte": "https://www.terabyteshop.com.br/hardware/placas-de-video"
}

# Configurações de paginação
PAGINATION = {
    "max_pages": 20,           # Máximo de páginas por scraper
    "page_size": 48,           # Produtos por página (quando aplicável)
    "kabum_page_size": 48,
    "pichau_page_size": 24,
    "terabyte_page_size": 20
}

# Delays e timeouts (em segundos)
TIMING = {
    "page_load_min": 1.5,      # Delay mínimo antes de carregar página
    "page_load_max": 3.5,      # Delay máximo antes de carregar página
    "scroll_min": 1.0,         # Delay mínimo após scroll
    "scroll_max": 2.0,         # Delay máximo após scroll
    "between_pages_min": 3.0,  # Delay mínimo entre páginas
    "between_pages_max": 6.0,  # Delay máximo entre páginas
    "selector_timeout": 15000, # Timeout para aguardar seletores (ms)
    "page_timeout": 30000,     # Timeout padrão de página (ms)
    "captcha_wait": 30         # Tempo de espera para resolver CAPTCHA
}

# Configurações de retry
RETRY = {
    "max_attempts": 3,         # Máximo de tentativas
    "initial_delay": 2,        # Delay inicial (segundos)
    "backoff_multiplier": 2    # Multiplicador para backoff exponencial
}

# User Agents (Chrome realistas)
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
]

# Viewports comuns
VIEWPORTS = [
    {"width": 1920, "height": 1080},
    {"width": 1366, "height": 768},
    {"width": 1536, "height": 864},
    {"width": 1440, "height": 900},
    {"width": 1280, "height": 720},
]

# Timezones brasileiros (timezone_id, latitude, longitude, cidade)
TIMEZONES = [
    ('America/Sao_Paulo', -23.5505, -46.6333, 'São Paulo'),
    ('America/Sao_Paulo', -22.9068, -43.1729, 'Rio de Janeiro'),
    ('America/Fortaleza', -3.7172, -38.5433, 'Fortaleza'),
    ('America/Manaus', -3.1190, -60.0217, 'Manaus'),
]

# Palavras-chave para detecção de CAPTCHA
CAPTCHA_KEYWORDS = [
    'challenge', 'captcha', 'verificação', 'cloudflare',
    'just a moment', 'checking your browser', 'ddos protection',
    'security check', 'verify you are human'
]

# Validação de preços
PRICE_VALIDATION = {
    "min_price": 100,          # Preço mínimo válido (R$)
    "max_price": 50000,        # Preço máximo válido (R$)
}

# Fabricantes conhecidos
KNOWN_BRANDS = [
    "ASUS", "MSI", "GIGABYTE", "GALAX", "XFX", "ASROCK", "ZOTAC", "PNY",
    "POWERCOLOR", "SAPPHIRE", "COLORFUL", "INNO3D", "PALIT", "EVGA",
    "PCYES", "MANCER", "GAINWARD", "AFOX", "BIOSTAR", "MANLI",
    "MAXSUN", "LEADTEK", "SPARKLE", "SUPERFRAME", "DUEX"
]

# Configurações de logging
LOGGING = {
    "level": "INFO",           # DEBUG, INFO, WARNING, ERROR
    "file": "scraper.log",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "console_colors": True
}

# Configurações de database
DATABASE = {
    "name": "prices.db",
    "backup_enabled": True,
    "backup_interval": 100     # Backup a cada N inserções
}
