from playwright.sync_api import sync_playwright

pesquisa = "airpods pro"
palavras = pesquisa.lower().split()
print(f"Palavras a pesquisar: {palavras}")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    pesquisa_url = f'%22{pesquisa.replace(" ", "+")}%22'
    page.goto(f"https://www.amazon.es/s?k={pesquisa_url}&language=pt_PT")
    page.wait_for_timeout(4000)
    items = page.query_selector_all("[data-component-type='s-search-result']")
    for item in items[:8]:
        nome_el = item.query_selector("h2 span")
        preco_el = item.query_selector(".a-price .a-offscreen")
        if nome_el and preco_el:
            nome = nome_el.inner_text()
            preco = preco_el.inner_text()
            nome_lower = nome.lower()
            match = all(p in nome_lower for p in palavras)
            print(f"{'✅' if match else '❌'} {nome[:50]} — {preco}")
            print(f"   palavras: {palavras}")
            print(f"   nome: {nome_lower[:60]}")
            print(f"   match: {match}")
            print()
    browser.close()