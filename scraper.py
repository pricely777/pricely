import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import time
import random

def scraper_produto(url, nome_loja):
    # Headers mais realistas para não ser bloqueado
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "pt-PT,pt;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
    }

    try:
        print(f"A procurar preço em {nome_loja}...")
        # Espera aleatória para não parecer um robot
        time.sleep(random.uniform(1, 3))

        sessao = requests.Session()
        resposta = sessao.get(url, headers=headers, timeout=15)
        resposta.raise_for_status()
        soup = BeautifulSoup(resposta.text, "html.parser")

        # Tenta encontrar o preço
        preco = None
        possiveis = soup.select("[class*='price'], [class*='preco'], [class*='valor'], [class*='Price']")
        for el in possiveis:
            texto = el.get_text(strip=True)
            if "€" in texto:
                preco = texto[:20]
                break

        # Tenta encontrar o título do produto
        titulo = None
        for tag in ["h1", "h2"]:
            el = soup.find(tag)
            if el:
                titulo = el.get_text(strip=True)[:60]
                break

        return {
            "loja": nome_loja,
            "url": url,
            "produto": titulo if titulo else "Não encontrado",
            "preco": preco if preco else "Não encontrado",
            "data": datetime.now().strftime("%Y-%m-%d %H:%M")
        }

    except Exception as e:
        return {
            "loja": nome_loja,
            "url": url,
            "produto": "Erro",
            "preco": f"Erro: {str(e)}",
            "data": datetime.now().strftime("%Y-%m-%d %H:%M")
        }

# ── Teste com produtos reais ────────────────────────────
if __name__ == "__main__":
    produtos = [
    ("https://www.kuantokusta.pt/informatica/portateis", "KuantoKusta"),
]

    resultados = []
    for url, loja in produtos:
        resultado = scraper_produto(url, loja)
        resultados.append(resultado)
        print(f"{resultado['loja']}: {resultado['produto']} — {resultado['preco']}")

    with open("resultados.json", "w", encoding="utf-8") as f:
        json.dump(resultados, f, ensure_ascii=False, indent=2)

    print("\nResultados guardados em resultados.json!")