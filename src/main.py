"""
GPU Price Scraper - CLI Entry Point

Provides command-line interface for running scrapers, viewing stats, and exporting data.
Uses ScraperFactory and SQLAlchemy ORM for all operations.
"""

import argparse
import asyncio
import sys
from datetime import datetime

from src.scrapers.factory import ScraperFactory
from src.backend.core.models import Store
from src.backend.core.database import create_tables, get_db_session
from src.backend.core.repository import ProductRepository
from src.utils.logger import get_logger

logger = get_logger(__name__)


def _format_duration(seconds: float) -> str:
    """Format duration in seconds to readable string"""
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


def _print_header(text: str, char: str = "=", width: int = 60) -> None:
    """Print formatted header"""
    print(char * width)
    print(f"{text:^{width}}")
    print(char * width)


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Scraper de preços de placas de vídeo de múltiplas lojas",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:
  python -m src.main                          # Executa todos os scrapers
  python -m src.main --scraper pichau         # Executa apenas Pichau
  python -m src.main --scraper kabum terabyte # Executa Kabum e Terabyte
  python -m src.main --headless               # Executa em modo headless
  python -m src.main --export csv             # Exporta resultados para CSV após scraping
        """,
    )

    parser.add_argument(
        "--scraper",
        "-s",
        nargs="+",
        choices=["pichau", "kabum", "terabyte", "all"],
        default=["all"],
        help="Scrapers para executar (padrão: all)",
    )

    parser.add_argument(
        "--headless",
        action="store_true",
        help="Executar em modo headless (sem interface gráfica)",
    )

    parser.add_argument(
        "--export", choices=["csv", "json", "both"], help="Exportar dados após scraping"
    )

    parser.add_argument(
        "--stats", action="store_true", help="Mostrar estatísticas do banco de dados"
    )

    return parser.parse_args()


def get_scrapers(scraper_names, headless=False):
    """
    Create scraper instances using ScraperFactory

    Args:
        scraper_names: List of scraper names to create
        headless: Whether to run in headless mode

    Returns:
        List of scraper instances
    """
    store_map = {
        "pichau": Store.PICHAU,
        "kabum": Store.KABUM,
        "terabyte": Store.TERABYTE,
    }

    # If 'all' is in the list, use all stores
    if "all" in scraper_names:
        scraper_names = ["pichau", "kabum", "terabyte"]

    scrapers = []
    for name in scraper_names:
        if name in store_map:
            scraper = ScraperFactory.create(store_map[name])
            scrapers.append(scraper)

    return scrapers


def main():
    """Main entry point"""
    args = parse_arguments()

    # Header
    _print_header("🛒 SCRAPER DE PREÇOS - PLACAS DE VÍDEO")
    print(f"⏰ Início: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🎯 Scrapers: {', '.join(args.scraper)}")
    print(f"👁️ Modo: {'Headless' if args.headless else 'Visual'}")
    print()

    # Ensure database tables exist
    logger.info("Inicializando banco de dados...")
    create_tables()

    # Show initial stats if requested
    if args.stats:
        print("\n📊 ESTATÍSTICAS INICIAIS")
        print("=" * 60)
        with get_db_session() as session:
            repo = ProductRepository(session)
            stats = repo.get_stats()
            for key, value in stats.items():
                print(f"  {key}: {value}")
        print()

    # Get scrapers via Factory
    scrapers = get_scrapers(args.scraper, headless=args.headless)

    if not scrapers:
        logger.error("Nenhum scraper válido selecionado!")
        sys.exit(1)

    # Execute scrapers
    start_time = datetime.now()
    successful = 0
    failed = 0

    async def run_async_scrapers():
        nonlocal successful, failed
        for scraper in scrapers:
            scraper_name = scraper.__class__.__name__.replace("Scraper", "")
            logger.info(f"Iniciando {scraper_name}...")

            try:
                await scraper.run()
                successful += 1
                logger.info(f"✅ {scraper_name} concluído com sucesso")
            except KeyboardInterrupt:
                logger.warning(f"⚠️ {scraper_name} interrompido pelo usuário")
                print("\n\n🛑 Execução interrompida pelo usuário")
                break
            except Exception as e:
                failed += 1
                logger.error(f"❌ Erro fatal em {scraper_name}: {e}")
                print(f"\n❌ Erro em {scraper_name}: {e}\n")

    try:
        asyncio.run(run_async_scrapers())
    except KeyboardInterrupt:
        pass

    # Calculate duration
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()

    # Final report
    print("\n" + "=" * 60)
    print("📊 RELATÓRIO FINAL")
    print("=" * 60)
    print(f"⏱️ Duração total: {_format_duration(duration)}")
    print(f"✅ Scrapers bem-sucedidos: {successful}")
    print(f"❌ Scrapers com falha: {failed}")
    print()

    # Database stats
    with get_db_session() as session:
        repo = ProductRepository(session)
        stats = repo.get_stats()
        print("📈 Estatísticas do Banco:")
        for key, value in stats.items():
            print(f"  • {key}: {value}")
        print()

        # Export if requested
        if args.export:
            print("📤 Exportando dados...")

            if args.export in ["csv", "both"]:
                csv_file = repo.export_to_csv()
                print(f"  ✓ CSV: {csv_file}")

            if args.export in ["json", "both"]:
                json_file = repo.export_to_json()
                print(f"  ✓ JSON: {json_file}")

            print()

    # Final message
    _print_header("✅ COLETA FINALIZADA")
    logger.info("Programa encerrado")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n🛑 Programa interrompido pelo usuário")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Erro fatal: {e}")
        sys.exit(1)
