"""
Teste detalhado do scraper Pichau para debug
"""
from playwright.sync_api import sync_playwright
from scrapers.pichau import PichauScraper
import database

# Cria banco
database.create_table()

print("=" * 60)
print("TESTE DETALHADO - PICHAU SCRAPER")
print("=" * 60)

with sync_playwright() as p:
    scraper = PichauScraper(headless=False)
    
    # Configura driver
    scraper.setup_driver(p)
    
    # Navega para primeira página
    url = "https://www.pichau.com.br/hardware/placa-de-video"
    print(f"\n1. Navegando para: {url}")
    
    try:
        loaded = scraper._load_page(url)
        print(f"   Página carregada: {loaded}")
    except Exception as e:
        print(f"   ERRO ao carregar: {e}")
        scraper.close()
        exit(1)
    
    # Verifica CAPTCHA
    print("\n2. Verificando CAPTCHA...")
    has_captcha = scraper._check_captcha()
    print(f"   CAPTCHA detectado: {has_captcha}")
    
    if has_captcha:
        print("   [!] CAPTCHA detectado, encerrando teste")
        scraper.close()
        exit(1)
    
    # Pega produtos
    print("\n3. Buscando produtos...")
    products = scraper._get_products()
    print(f"   Produtos encontrados: {len(products)}")
    
    if not products:
        print("   [!] Nenhum produto encontrado!")
        scraper.close()
        exit(1)
    
    # Testa extração do primeiro produto
    print("\n4. Testando extração do primeiro produto...")
    first_product = products[0]
    
    # Link
    print("\n   4.1. Extraindo link...")
    link = scraper._extract_link(first_product)
    print(f"        Link: {link}")
    
    # Título
    print("\n   4.2. Extraindo título...")
    title = scraper._extract_title(first_product)
    print(f"        Título: {title}")
    
    # Preço
    print("\n   4.3. Extraindo preço...")
    price_str, price_num = scraper._extract_price(first_product)
    print(f"        Preço String: {price_str}")
    print(f"        Preço Numérico: {price_num}")
    
    # Dados completos
    print("\n   4.4. Extraindo dados completos...")
    data = scraper._extract_product_data(first_product)
    
    if data:
        print("        [OK] Dados extraídos:")
        for key, value in data.items():
            print(f"          {key}: {value}")
    else:
        print("        [ERRO] Falha ao extrair dados!")
    
    # Validação
    print("\n   4.5. Validando dados...")
    is_valid = scraper._validate_product_data(data)
    print(f"        Válido: {is_valid}")
    
    if not is_valid:
        print("        [!] Dados inválidos! Verificando motivo...")
        if not data:
            print("            - data é None")
        elif not data.get("Produto") or data["Produto"] == "Sem Titulo":
            print(f"            - Título inválido: {data.get('Produto')}")
        elif not data.get("Link"):
            print(f"            - Link inválido: {data.get('Link')}")
        else:
            price = data.get("Preco_Numerico", 0)
            from config import PRICE_VALIDATION
            if price < PRICE_VALIDATION['min_price']:
                print(f"            - Preço muito baixo: {price} < {PRICE_VALIDATION['min_price']}")
            elif price > PRICE_VALIDATION['max_price']:
                print(f"            - Preço muito alto: {price} > {PRICE_VALIDATION['max_price']}")
    
    # Tenta salvar
    if data and is_valid:
        print("\n   4.6. Salvando no banco...")
        saved = scraper.save_product(data)
        print(f"        Salvo: {saved}")
    
    # Processa todos os produtos
    print(f"\n5. Processando todos os {len(products)} produtos...")
    items_saved = scraper._process_products(products)
    print(f"   Total salvos: {items_saved}")
    
    # Estatísticas do banco
    print("\n6. Verificando banco de dados...")
    stats = database.get_stats()
    print(f"   Total de produtos no banco: {stats.get('total_produtos', 0)}")
    
    print("\n" + "=" * 60)
    print("Pressione Enter para fechar...")
    input()
    
    scraper.close()
