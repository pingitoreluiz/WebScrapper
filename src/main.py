from playwright.sync_api import sync_playwright
from src.scrapers.kabum import KabumScraper
from src.scrapers.terabyte import TerabyteScraper
from src.scrapers.pichau import PichauScraper
import src.database as database
import argparse
import sys
from datetime import datetime
from src.legacy_utils import setup_logger, print_header, print_stats, format_duration

def parse_arguments():
    """Parse argumentos da linha de comando"""
    parser = argparse.ArgumentParser(
        description='Scraper de preços de placas de vídeo de múltiplas lojas',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:
  python main.py                          # Executa todos os scrapers
  python main.py --scraper pichau         # Executa apenas Pichau
  python main.py --scraper kabum terabyte # Executa Kabum e Terabyte
  python main.py --headless               # Executa em modo headless
  python main.py --export csv             # Exporta resultados para CSV após scraping
        """
    )
    
    parser.add_argument(
        '--scraper', '-s',
        nargs='+',
        choices=['pichau', 'kabum', 'terabyte', 'all'],
        default=['all'],
        help='Scrapers para executar (padrão: all)'
    )
    
    parser.add_argument(
        '--headless',
        action='store_true',
        help='Executar em modo headless (sem interface gráfica)'
    )
    
    parser.add_argument(
        '--export',
        choices=['csv', 'json', 'both'],
        help='Exportar dados após scraping'
    )
    
    parser.add_argument(
        '--stats',
        action='store_true',
        help='Mostrar estatísticas do banco de dados'
    )
    
    return parser.parse_args()


def get_scrapers(scraper_names, headless=False):
    """
    Retorna lista de scrapers baseado nos nomes
    
    Args:
        scraper_names: Lista de nomes de scrapers
        headless: Se deve executar em modo headless
        
    Returns:
        Lista de instâncias de scrapers
    """
    scraper_map = {
        'pichau': PichauScraper,
        'kabum': KabumScraper,
        'terabyte': TerabyteScraper
    }
    
    # Se 'all' está na lista, retorna todos
    if 'all' in scraper_names:
        scraper_names = ['pichau', 'kabum', 'terabyte']
    
    scrapers = []
    for name in scraper_names:
        if name in scraper_map:
            scrapers.append(scraper_map[name](headless=headless))
    
    return scrapers


def main():
    """Função principal"""
    args = parse_arguments()
    
    # Setup logger
    logger = setup_logger('main', level='INFO')
    
    # Cabeçalho
    print_header("🛒 SCRAPER DE PREÇOS - PLACAS DE VÍDEO")
    print(f"⏰ Início: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🎯 Scrapers: {', '.join(args.scraper)}")
    print(f"👁️ Modo: {'Headless' if args.headless else 'Visual'}")
    print()
    
    # Garante que o banco existe
    logger.info("Inicializando banco de dados...")
    database.create_table()
    
    # Mostra estatísticas iniciais se solicitado
    if args.stats:
        print("\n📊 ESTATÍSTICAS INICIAIS")
        print("=" * 60)
        stats = database.get_stats()
        for key, value in stats.items():
            print(f"  {key}: {value}")
        print()
    
    # Obtém scrapers
    scrapers = get_scrapers(args.scraper, headless=args.headless)
    
    if not scrapers:
        logger.error("Nenhum scraper válido selecionado!")
        sys.exit(1)
    
    # Executa scrapers
    start_time = datetime.now()
    successful = 0
    failed = 0
    
    # Executa scrapers
    start_time = datetime.now()
    successful = 0
    failed = 0
    
    # Run async
    import asyncio
    
    async def run_async_scrapers():
        nonlocal successful, failed
        for scraper in scrapers:
            scraper_name = scraper.__class__.__name__.replace('Scraper', '')
            logger.info(f"Iniciando {scraper_name}...")
            
            try:
                # The run method is now async and handles its own browser resource management
                # It does not take arguments
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
    
    # Calcula duração
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    # Estatísticas finais
    print("\n" + "=" * 60)
    print("📊 RELATÓRIO FINAL")
    print("=" * 60)
    print(f"⏱️ Duração total: {format_duration(duration)}")
    print(f"✅ Scrapers bem-sucedidos: {successful}")
    print(f"❌ Scrapers com falha: {failed}")
    print()
    
    # Estatísticas do banco
    stats = database.get_stats()
    print("📈 Estatísticas do Banco:")
    for key, value in stats.items():
        print(f"  • {key}: {value}")
    print()
    
    # Exportação se solicitada
    if args.export:
        print("📤 Exportando dados...")
        
        if args.export in ['csv', 'both']:
            csv_file = database.export_to_csv()
            print(f"  ✓ CSV: {csv_file}")
        
        if args.export in ['json', 'both']:
            json_file = database.export_to_json()
            print(f"  ✓ JSON: {json_file}")
        
        print()
    
    # Mensagem final
    print_header("✅ COLETA FINALIZADA")
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
