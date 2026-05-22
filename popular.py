import asyncio
from scraper_avancado import scraper_todas_lojas

produtos = [
    "samsung galaxy a55",
    "samsung galaxy a35",
    "xiaomi redmi note 13",
    "xiaomi 14",
    "google pixel 8",
    "oneplus 12",
    "motorola edge 50",
    "iphone 13",
    "iphone 16",
    "samsung galaxy s25",
]

async def main():
    for produto in produtos:
        print(f"\n{'='*40}")
        print(f"A pesquisar: {produto}")
        print('='*40)
        await scraper_todas_lojas(produto)

asyncio.run(main())