from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from playwright.async_api import async_playwright
from datetime import datetime

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

async def scraper_amazon(pagina, pesquisa):
    await pagina.goto(f"https://www.amazon.es/s?k={pesquisa.replace(' ','+')}&language=pt_PT")
    await pagina.wait_for_timeout(4000)
    produtos = await pagina.query_selector_all("[data-component-type='s-search-result']")
    resultados = []
    for produto in produtos[:8]:
        try:
            nome_el = await produto.query_selector("h2 span")
            nome = await nome_el.inner_text() if nome_el else None
            preco_el = await produto.query_selector(".a-price .a-offscreen")
            preco = await preco_el.inner_text() if preco_el else None
            if nome and preco:
                preco_num = float(preco.replace("€","").replace(".","").replace(",",".").strip())
                resultados.append({
                    "loja": "Amazon.es",
                    "produto": nome[:60],
                    "preco": preco,
                    "preco_num": preco_num,
                    "data": datetime.now().strftime("%Y-%m-%d %H:%M")
                })
        except:
            continue
    return resultados

@app.get("/")
def root():
    return {"status": "Pricely API online"}

@app.get("/pesquisar")
async def pesquisar(q: str):
    async with async_playwright() as p:
browser = await p.chromium.launch(headless=False)
        pagina = await browser.new_page()
        resultados = []
        try:
            r = await scraper_amazon(pagina, q)
            resultados.extend(r)
        except Exception as e:
            print(f"Erro: {e}")
        await browser.close()
    resultados.sort(key=lambda x: x["preco_num"])
    return {"resultados": resultados, "total": len(resultados)}