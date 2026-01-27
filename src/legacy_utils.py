"""
Utilitários compartilhados para o projeto de scraping
"""
import logging
import re
from datetime import datetime
from colorama import Fore, Style, init

# Inicializa colorama para Windows
init(autoreset=True)

class ColoredFormatter(logging.Formatter):
    """Formatter customizado com cores"""
    
    COLORS = {
        'DEBUG': Fore.CYAN,
        'INFO': Fore.GREEN,
        'WARNING': Fore.YELLOW,
        'ERROR': Fore.RED,
        'CRITICAL': Fore.RED + Style.BRIGHT,
    }
    
    def format(self, record):
        levelname = record.levelname
        if levelname in self.COLORS:
            record.levelname = f"{self.COLORS[levelname]}{levelname}{Style.RESET_ALL}"
        return super().format(record)


def setup_logger(name, log_file='scraper.log', level=logging.INFO, console_colors=True):
    """
    Configura logger com output para arquivo e console
    
    Args:
        name: Nome do logger
        log_file: Arquivo de log
        level: Nível de logging
        console_colors: Se deve usar cores no console
        
    Returns:
        Logger configurado
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Remove handlers existentes
    logger.handlers = []
    
    # Handler para arquivo
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(level)
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    
    # Handler para console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    
    if console_colors:
        console_formatter = ColoredFormatter(
            '%(levelname)s - %(message)s'
        )
    else:
        console_formatter = logging.Formatter('%(levelname)s - %(message)s')
    
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    return logger


def clean_price(price_str):
    """
    Converte string de preço para float
    
    Args:
        price_str: String com preço (ex: "R$ 2.500,00")
        
    Returns:
        Float com valor numérico
    """
    try:
        # Remove R$, espaços e converte separadores
        clean = price_str.replace("R$", "").replace(".", "").replace(",", ".").strip()
        return float(clean)
    except:
        return 0.0


def extract_chip_brand(title, link=""):
    """
    Extrai marca do chip (NVIDIA, AMD, Intel) do título
    
    Args:
        title: Título do produto
        link: URL do produto (opcional)
        
    Returns:
        String com marca do chip
    """
    title_upper = title.upper()
    
    if "GEFORCE" in title_upper or "RTX" in title_upper or "GTX" in title_upper or "NVIDIA" in title_upper:
        return "NVIDIA"
    elif "RADEON" in title_upper or "RX" in title_upper or "AMD" in title_upper:
        return "AMD"
    elif "ARC" in title_upper or "INTEL" in title_upper:
        return "INTEL"
    else:
        return "Outros"


def extract_manufacturer(title, link="", known_brands=None):
    """
    Extrai fabricante (ASUS, MSI, etc) do título ou link
    
    Args:
        title: Título do produto
        link: URL do produto
        known_brands: Lista de fabricantes conhecidos
        
    Returns:
        String com nome do fabricante
    """
    if known_brands is None:
        from config import KNOWN_BRANDS
        known_brands = KNOWN_BRANDS
    
    title_upper = title.upper()
    link_lower = link.lower() if link else ""
    
    # Tenta primeiro no título
    for brand in known_brands:
        if brand in title_upper:
            return brand
    
    # Se não achou no título, tenta no link
    if link_lower:
        for brand in known_brands:
            brand_lower = brand.lower()
            if f"-{brand_lower}-" in link_lower or f"/{brand_lower}-" in link_lower:
                return brand
    
    return "Genérica/Outra"


def extract_model(title):
    """
    Extrai modelo da GPU (RTX 4090, RX 7900 XT, etc) do título
    
    Args:
        title: Título do produto
        
    Returns:
        String com modelo da GPU
    """
    title_upper = title.upper()
    
    # NVIDIA (RTX/GTX)
    nvidia_match = re.search(r'(RTX|GTX)\s*(\d{3,4})\s*(TI|SUPER)?', title_upper)
    if nvidia_match:
        p1, p2, p3 = nvidia_match.groups()
        return f"{p1} {p2}" + (f" {p3}" if p3 else "")
    
    # AMD (RX)
    amd_match = re.search(r'(RX)\s*(\d{3,4})\s*(XT|XTX|GRE)?', title_upper)
    if amd_match:
        p1, p2, p3 = amd_match.groups()
        return f"{p1} {p2}" + (f" {p3}" if p3 else "")
    
    # Intel (ARC)
    intel_match = re.search(r'(ARC)\s*(A\d{3})', title_upper)
    if intel_match:
        p1, p2 = intel_match.groups()
        return f"{p1} {p2}"
    
    return "Desconhecido"


def validate_product_data(data, min_price=100, max_price=50000):
    """
    Valida se os dados do produto são válidos
    
    Args:
        data: Dicionário com dados do produto
        min_price: Preço mínimo válido
        max_price: Preço máximo válido
        
    Returns:
        Boolean indicando se dados são válidos
    """
    if not data:
        return False
    
    # Verifica campos obrigatórios
    if not data.get("Produto") or data["Produto"] == "Sem Titulo":
        return False
    
    if not data.get("Link"):
        return False
    
    # Valida preço
    price = data.get("Preco_Numerico", 0)
    if price <= 0 or price < min_price or price > max_price:
        return False
    
    return True


def format_duration(seconds):
    """
    Formata duração em segundos para string legível
    
    Args:
        seconds: Duração em segundos
        
    Returns:
        String formatada (ex: "2m 30s")
    """
    if seconds < 60:
        return f"{seconds:.0f}s"
    elif seconds < 3600:
        minutes = seconds // 60
        secs = seconds % 60
        return f"{minutes:.0f}m {secs:.0f}s"
    else:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{hours:.0f}h {minutes:.0f}m"


def print_header(text, char="=", width=60):
    """
    Imprime cabeçalho formatado
    
    Args:
        text: Texto do cabeçalho
        char: Caractere para bordas
        width: Largura total
    """
    print(char * width)
    print(f"{text:^{width}}")
    print(char * width)


def print_stats(stats_dict):
    """
    Imprime estatísticas formatadas
    
    Args:
        stats_dict: Dicionário com estatísticas
    """
    print("\n" + "=" * 60)
    print("📊 ESTATÍSTICAS")
    print("=" * 60)
    
    for key, value in stats_dict.items():
        print(f"  {key}: {value}")
    
    print("=" * 60)


class ProgressTracker:
    """Rastreador de progresso simples"""
    
    def __init__(self, total=0, description="Processando"):
        self.total = total
        self.current = 0
        self.description = description
        self.start_time = datetime.now()
    
    def update(self, n=1):
        """Atualiza progresso"""
        self.current += n
        if self.total > 0:
            percentage = (self.current / self.total) * 100
            print(f"\r{self.description}: {self.current}/{self.total} ({percentage:.1f}%)", end="")
        else:
            print(f"\r{self.description}: {self.current}", end="")
    
    def finish(self):
        """Finaliza progresso"""
        elapsed = (datetime.now() - self.start_time).total_seconds()
        print(f"\n✅ Concluído em {format_duration(elapsed)}")
