import streamlit as st
import json
import os

st.set_page_config(page_title="Pricely", page_icon="📊", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
.stApp { background-color: #0D0D0D; color: #F0EDE6; }
[data-testid="stSidebar"] { background-color: #111111; border-right: 1px solid #222; }
[data-testid="stMetric"] { background: #1A1A1A; border: 1px solid #222; border-radius: 8px; padding: 20px; }
[data-testid="stMetricValue"] { color: #4A9EF5 !important; font-size: 2rem !important; font-weight: 700 !important; }
[data-testid="stMetricLabel"] { color: #666 !important; font-size: 0.75rem !important; text-transform: uppercase; }
.stButton > button { background: #4A9EF5 !important; color: #000 !important; font-weight: 700 !important; border: none !important; border-radius: 4px !important; }
hr { border-color: #222 !important; }
.produto-card { background: #1A1A1A; border: 1px solid #222; border-radius: 8px; padding: 16px 20px; margin-bottom: 8px; display: flex; justify-content: space-between; align-items: center; }
.produto-card.melhor { border-left: 3px solid #4A9EF5; background: rgba(74,158,245,0.05); }
.produto-card.pior { border-left: 3px solid #F03E3E; background: rgba(240,62,62,0.03); }
#MainMenu, footer, header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("<div style='font-family:Georgia,serif;font-size:1.6rem;font-weight:700;color:#F0EDE6;padding:8px 0;'>Pricely</div>", unsafe_allow_html=True)
    st.markdown("---")
    pagina = st.radio("", ["Dashboard", "Pesquisar", "Historico"], label_visibility="collapsed")
    st.markdown("---")
    st.success("Online")

dados = []
if os.path.exists("resultados.json"):
    with open("resultados.json", "r", encoding="utf-8") as f:
        dados = json.load(f)

if pagina == "Dashboard":
    st.markdown("# Dashboard")
    st.divider()
    total = len(dados)
    lojas = len(set(d["loja"] for d in dados)) if dados else 0
    preco_min = min(d["preco_num"] for d in dados) if dados else 0
    preco_max = max(d["preco_num"] for d in dados) if dados else 0
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Produtos", total)
    col2.metric("Lojas", lojas)
    col3.metric("Melhor preco", f"{preco_min:.2f} EUR" if preco_min else "---")
    col4.metric("Diferenca", f"{preco_max - preco_min:.2f} EUR" if dados else "---")
    st.divider()
    if dados:
        for item in dados:
            e_melhor = item["preco_num"] == preco_min
            diff = item["preco_num"] - preco_min
            badge = "MELHOR PRECO" if e_melhor else f"+{diff:.2f} EUR"
            cor = "#4A9EF5" if e_melhor else "#F03E3E"
            classe = "melhor" if e_melhor else ""
            st.markdown(f"""<div class="produto-card {classe}"><div><div style="font-weight:600">{item["produto"]}</div><div style="color:#666;font-size:0.75rem">{item["loja"]} · {item["data"]}</div></div><div style="text-align:right"><div style="font-size:1.2rem;font-weight:700">{item["preco"]}</div><div style="color:{cor};font-size:0.7rem">{badge}</div></div></div>""", unsafe_allow_html=True)
    else:
        st.info("Vai a Pesquisar para comecar.")

elif pagina == "Pesquisar":
    st.markdown("# Pesquisar")
    st.divider()
    pesquisa = st.text_input("Produto", placeholder="ex: iPhone 15...")
    if st.button("Pesquisar") and pesquisa:
        with st.spinner("A pesquisar..."):
            os.system("python scraper_avancado.py")
        st.success("Concluido!")
        st.rerun()
    if dados:
        preco_min = min(d["preco_num"] for d in dados)
        for item in dados:
            e_melhor = item["preco_num"] == preco_min
            diff = item["preco_num"] - preco_min
            badge = "MELHOR PRECO" if e_melhor else f"+{diff:.2f} EUR"
            cor = "#4A9EF5" if e_melhor else "#F03E3E"
            classe = "melhor" if e_melhor else ""
            st.markdown(f"""<div class="produto-card {classe}"><div><div style="font-weight:600">{item["produto"]}</div><div style="color:#666;font-size:0.75rem">{item["loja"]}</div></div><div style="text-align:right"><div style="font-size:1.2rem;font-weight:700">{item["preco"]}</div><div style="color:{cor};font-size:0.7rem">{badge}</div></div></div>""", unsafe_allow_html=True)

elif pagina == "Historico":
    st.markdown("# Historico")
    st.divider()
    st.info("Em breve.")