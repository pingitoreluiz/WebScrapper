"""
Script de debug para verificar estrutura HTML e seletores
"""

from playwright.sync_api import sync_playwright
import time


def debug_pichau():
    print("=" * 60)
    print("DEBUG: Pichau")
    print("=" * 60)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        url = "https://www.pichau.com.br/hardware/placa-de-video"
        print(f"\n1. Navegando para: {url}")
        page.goto(url, wait_until="domcontentloaded")

        time.sleep(5)

        # Verifica CAPTCHA
        print("\n2. Verificando conteúdo da página...")
        content = page.content().lower()

        captcha_keywords = [
            "challenge",
            "captcha",
            "verificação",
            "cloudflare",
            "just a moment",
        ]
        found_keywords = [kw for kw in captcha_keywords if kw in content]

        if found_keywords:
            print(f"   [!] Keywords encontradas: {found_keywords}")
        else:
            print("   [OK] Nenhuma keyword de CAPTCHA encontrada")

        # Verifica título da página
        title = page.title()
        print(f"\n3. Título da página: {title}")

        # Testa seletores de produtos
        print("\n4. Testando seletores de produtos...")
        selectors = [
            "article[data-cy*='product']",
            "div[data-cy*='product-card']",
            "div[class*='ProductCard']",
            "a[class*='product-card']",
            "div.MuiCard-root",
            "article[class*='product']",
        ]

        for selector in selectors:
            try:
                elements = page.locator(selector).all()
                print(f"   {selector}: {len(elements)} elementos")
                if len(elements) > 0:
                    print(f"      [OK] Seletor funciona!")
            except Exception as e:
                print(f"   {selector}: ERRO - {e}")

        # Pega primeiro produto e analisa
        print("\n5. Analisando primeiro produto...")

        # Tenta encontrar produtos
        products = None
        working_selector = None

        for selector in selectors:
            try:
                prods = page.locator(selector).all()
                if len(prods) > 0:
                    products = prods
                    working_selector = selector
                    break
            except:
                continue

        if products and len(products) > 0:
            print(f"   Usando seletor: {working_selector}")
            first = products[0]

            # Extrai HTML do primeiro produto
            html = first.inner_html()
            print(f"\n   HTML do primeiro produto (primeiros 500 chars):")
            print(f"   {html[:500]}...")

            # Tenta extrair preço
            print("\n6. Testando extração de preço...")
            price_selectors = [
                "div[class*='price']",
                "span[class*='price']",
                "p[class*='price']",
                "div[data-cy*='price']",
                "strong[class*='price']",
            ]

            for sel in price_selectors:
                try:
                    price_els = first.locator(sel).all()
                    if price_els:
                        for idx, pel in enumerate(price_els):
                            text = pel.inner_text().strip()
                            print(f"   {sel} [{idx}]: {text}")
                except Exception as e:
                    print(f"   {sel}: ERRO - {e}")

            # Texto completo do produto
            print("\n7. Texto completo do primeiro produto:")
            full_text = first.inner_text()
            print(f"   {full_text[:300]}...")

        else:
            print("   [ERRO] Nenhum produto encontrado!")

        print("\n" + "=" * 60)
        print("Pressione Enter para fechar o navegador...")
        input()

        browser.close()


if __name__ == "__main__":
    debug_pichau()
