import asyncio
from playwright.async_api import async_playwright

async def inspecionar():
    print("A iniciar browser...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        pagina = await browser.new_page()
        
        print("A abrir Amazon...")
        await pagina.goto("https://www.amazon.es/s?k=iphone+15&language=pt_PT")
        
        print("A aguardar carregamento...")
        await pagina.wait_for_timeout(5000)
        
        # Selectores específicos da Amazon
        produtos = await pagina.query_selector_all("[data-component-type='s-search-result']")
        
        print(f"\nProdutos encontrados: {len(produtos)}")
        
        resultados = []
        for produto in produtos[:8]:
            try:
                # Nome
                nome_el = await produto.query_selector("h2 span")
                nome = await nome_el.inner_text() if nome_el else "Sem nome"
                
                # Preço
                preco_el = await produto.query_selector(".a-price .a-offscreen")
                preco = await preco_el.inner_text() if preco_el else "Sem preço"
                
                if preco != "Sem preço":
                    resultados.append({"nome": nome[:50], "preco": preco})
                    print(f"  → {nome[:50]} — {preco}")
            except:
                continue
        
        await browser.close()
        print(f"\nTotal: {len(resultados)} produtos com preço!")

asyncio.run(inspecionar())