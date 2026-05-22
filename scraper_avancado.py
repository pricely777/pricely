import asyncio
from playwright.async_api import async_playwright
from datetime import datetime
import httpx
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ── Configuração ──────────────────────────────────────
SUPABASE_URL = "https://umejembwtzlsmedvwcgi.supabase.co"
SUPABASE_KEY = "sb_publishable_yA4ZIzW8YeDZ0hTs6Lj0ZA_sYkIEvQe"
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

EMAIL_REMETENTE = "pricelyplus@gmail.com"
EMAIL_PASSWORD = "dbsdfyyehfjgpeuv"
EMAIL_DONO = "newo26954@gmail.com"

# ── Palavras a excluir por pesquisa ───────────────────
EXCLUSOES = {
    "iphone 13": ["pro", "plus", "max"],
    "iphone 14": ["pro", "plus", "max"],
    "iphone 15": ["pro", "plus", "max"],
    "iphone 15 pro": ["max"],
    "iphone 16": ["pro", "plus", "max"],
    "samsung galaxy s24": ["ultra", "fe"],
    "samsung galaxy s25": ["ultra", "fe"],
    "airpods": ["max"],
    "airpods max": [],
    "airpods pro": [],
}


# ── Email ─────────────────────────────────────────────
def enviar_alerta(destinatario, produto, preco_antigo, preco_novo, loja):
    diferenca = preco_novo - preco_antigo
    sinal = "baixou" if diferenca < 0 else "subiu"
    assunto = f"Pricely: {produto[:30]} {sinal} em {loja}"
    corpo = f"""
    <html><body style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;">
        <div style="background:#0A3D2B;padding:24px;text-align:center;">
            <h1 style="color:white;margin:0;">Pricely</h1>
            <p style="color:rgba(255,255,255,0.7);margin:8px 0 0;">Alerta de preço</p>
        </div>
        <div style="padding:32px;background:#f9f9f9;">
            <h2>Mudança de preço detectada!</h2>
            <p><strong>Produto:</strong> {produto}</p>
            <p><strong>Loja:</strong> {loja}</p>
            <p><strong>Preço anterior:</strong> {preco_antigo:.2f} €</p>
            <p><strong>Preço actual:</strong> {preco_novo:.2f} €</p>
            <p style="color:{'green' if diferenca < 0 else 'red'};font-size:18px;font-weight:bold;">
                {sinal} {abs(diferenca):.2f} €
            </p>
            <a href="https://pricely-frontend-self.vercel.app"
               style="background:#0A3D2B;color:white;padding:14px 32px;
                      text-decoration:none;border-radius:4px;font-weight:bold;">
                Ver no Pricely
            </a>
        </div>
    </body></html>
    """
    msg = MIMEMultipart("alternative")
    msg["Subject"] = assunto
    msg["From"] = EMAIL_REMETENTE
    msg["To"] = destinatario
    msg.attach(MIMEText(corpo, "html"))
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as s:
            s.login(EMAIL_REMETENTE, EMAIL_PASSWORD)
            s.sendmail(EMAIL_REMETENTE, destinatario, msg.as_string())
        print(f"✅ Alerta enviado para {destinatario}!")
    except Exception as e:
        print(f"❌ Erro email: {e}")


# ── Supabase ──────────────────────────────────────────
async def buscar_precos_anteriores(pesquisa):
    pesquisa_url = pesquisa.replace(" ", "%20")
    async with httpx.AsyncClient() as client:
        r = await client.get(
            f"{SUPABASE_URL}/rest/v1/produtos?pesquisa=eq.{pesquisa_url}",
            headers=HEADERS
        )
        if r.status_code == 200 and r.json():
            dados = {p["produto"]: p["preco_num"] for p in r.json()}
            print(f"  Preços anteriores encontrados: {len(dados)}")
            return dados
        print(f"  Sem preços anteriores")
        return {}


async def apagar_supabase(pesquisa):
    pesquisa_url = pesquisa.replace(" ", "%20")
    async with httpx.AsyncClient() as client:
        await client.delete(
            f"{SUPABASE_URL}/rest/v1/produtos?pesquisa=eq.{pesquisa_url}",
            headers=HEADERS
        )


async def guardar_supabase(resultados, pesquisa):
    async with httpx.AsyncClient() as client:
        for r in resultados:
            r["pesquisa"] = pesquisa
            await client.post(
                f"{SUPABASE_URL}/rest/v1/produtos",
                headers=HEADERS,
                json=r
            )
    print(f"✅ {len(resultados)} produtos guardados!")


# ── Scraper ───────────────────────────────────────────
async def scraper_amazon(pagina, pesquisa):
    print("A pesquisar na Amazon...")

    pesquisa_url = f'%22{pesquisa.replace(" ", "+")}%22'
    await pagina.goto(f"https://www.amazon.es/s?k={pesquisa_url}&language=pt_PT")
    await pagina.wait_for_timeout(4000)

    produtos = await pagina.query_selector_all("[data-component-type='s-search-result']")
    resultados = []

    excluir = EXCLUSOES.get(pesquisa.lower(), [])

    for produto in produtos[:12]:
        try:
            nome_el = await produto.query_selector("h2 span")
            nome = await nome_el.inner_text() if nome_el else None
            preco_el = await produto.query_selector(".a-price .a-offscreen")
            preco = await preco_el.inner_text() if preco_el else None

            if nome and preco:
                try:
                    preco_num_temp = float(preco.replace("€","").replace(".","").replace(",",".").strip())
                except:
                    continue

                if preco_num_temp < 20:
                    continue

                palavras = pesquisa.lower().split()
                nome_lower = nome.lower()
                if not all(p in nome_lower for p in palavras):
                    continue

                if any(e in nome_lower for e in excluir):
                    continue

                resultados.append({
                    "loja": "Amazon.es",
                    "produto": nome[:60],
                    "preco": preco,
                    "preco_num": preco_num_temp,
                    "data": datetime.now().strftime("%Y-%m-%d %H:%M")
                })
        except:
            continue
    return resultados


# ── Pipeline completo ─────────────────────────────────
async def scraper_todas_lojas(pesquisa, email_cliente=None):
    print(f"A pesquisar '{pesquisa}'...")

    precos_anteriores = await buscar_precos_anteriores(pesquisa)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        pagina = await browser.new_page()

        resultados = []
        try:
            r = await scraper_amazon(pagina, pesquisa)
            resultados.extend(r)
            print(f"  Amazon: {len(r)} produtos")
        except Exception as e:
            print(f"  Erro: {e}")

        await browser.close()

    resultados.sort(key=lambda x: x["preco_num"])

    if precos_anteriores:
        for produto in resultados:
            nome = produto["produto"]
            preco_novo = produto["preco_num"]
            if nome in precos_anteriores:
                preco_antigo = precos_anteriores[nome]
                diferenca = abs(preco_novo - preco_antigo)
                print(f"  {nome[:30]} — anterior: {preco_antigo}€ novo: {preco_novo}€ diff: {diferenca:.2f}€")
                if diferenca > 1:
                    print(f"⚠️ Preço mudou!")
                    enviar_alerta(EMAIL_DONO, nome, preco_antigo, preco_novo, produto["loja"])
                    if email_cliente:
                        enviar_alerta(email_cliente, nome, preco_antigo, preco_novo, produto["loja"])

    await apagar_supabase(pesquisa)
    await guardar_supabase(resultados, pesquisa)
    return resultados


if __name__ == "__main__":
    pesquisa = input("Produto a pesquisar: ")
    asyncio.run(scraper_todas_lojas(pesquisa))