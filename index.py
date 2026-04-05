import streamlit as st
import pandas as pd
import requests
import os
from streamlit_gsheets import GSheetsConnection

# --- CONFIGURAÇÃO DA PÁGINA (Identidade Independente) ---
st.set_page_config(page_title="Portal Nacional de Oportunidades", page_icon="💼", layout="wide")

# --- ESTILIZAÇÃO CUSTOMIZADA (CSS) ---
st.markdown("""
    <style>
    .vaga-card {
        background-color: #ffffff;
        padding: 25px;
        border-radius: 15px;
        border-left: 8px solid #2ecc71;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        margin-bottom: 20px;
        border: 1px solid #eee;
    }
    .titulo-vaga { color: #1e3799; font-size: 22px; font-weight: bold; margin-bottom: 5px; }
    .empresa-vaga { color: #4b6584; font-size: 18px; font-weight: 500; margin-bottom: 10px; }
    .tag {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: bold;
        margin-right: 8px;
        margin-bottom: 5px;
    }
    .tag-local { background-color: #d1d8e0; color: #2d3436; }
    .tag-tipo { background-color: #c7ecee; color: #0984e3; }
    .tag-fonte { background-color: #f8c291; color: #e67e22; }
    .valor-vaga { color: #27ae60; font-weight: bold; font-size: 16px; margin-top: 10px; }
    </style>
""", unsafe_allow_html=True)

# --- FUNÇÕES DE CAPTAÇÃO DE DADOS ---

@st.cache_data(ttl=600)
def carregar_vagas_integradas():
    lista_final = []

    # 1. GOOGLE SHEETS (Base Interna)
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        df_sheets = conn.read()
        df_sheets = df_sheets.dropna(how="all")
        
        for _, row in df_sheets.iterrows():
            if str(row.get('Status', '')).lower() == 'inativa':
                continue
            lista_final.append({
                "titulo": str(row.get('Título', 'Vaga Sem Título')),
                "empresa": str(row.get('Empresa', 'Indústria Brasileira')),
                "cidade": str(row.get('Cidade', 'Brasil')),
                "uf": str(row.get('UF', 'BR')),
                "tipo": str(row.get('Tipo', 'Presencial')),
                "salario": row.get('Salário', 0),
                "nivel": str(row.get('Área', 'Geral')),
                "fonte": "Interna",
                "link": str(row.get('Link_Inscrição', '#'))
            })
    except Exception as e:
        st.sidebar.error(f"⚠️ Erro Sheets: {e}")

    # 2. ADZUNA API (Brasil Todo)
    try:
        aid = st.secrets["APP_ID"]
        akey = st.secrets["APP_KEY"]
        # Busca Nacional por Indústria, Tecnologia e Ensino
        url_adz = f"https://api.adzuna.com/v1/api/jobs/br/search/1?app_id={aid}&app_key={akey}&results_per_page=30&what=industria%20tecnologia%20ensino&where=Brasil"
        res_adz = requests.get(url_adz).json()
        for item in res_adz.get('results', []):
            lista_final.append({
                "titulo": item.get('title'),
                "empresa": item.get('company', {}).get('display_name', 'Confidencial'),
                "cidade": item.get('location', {}).get('display_name', 'Brasil'),
                "uf": "BR",
                "tipo": "Remoto" if "remoto" in item.get('description', '').lower() else "Presencial",
                "salario": item.get('salary_min', 0),
                "nivel": "Mercado",
                "fonte": "Adzuna",
                "link": item.get('redirect_url')
            })
    except: pass

    # 3. GOOGLE JOBS (via SerpApi - Escala Nacional)
    try:
        serp_key = st.secrets.get("SERPAPI_KEY")
        if serp_key:
            url_serp = f"https://serpapi.com/search.json?engine=google_jobs&q=vagas+industria+brasil&hl=pt&gl=br&api_key={serp_key}"
            res_serp = requests.get(url_serp).json()
            for item in res_serp.get('jobs_results', []):
                lista_final.append({
                    "titulo": item.get('title'),
                    "empresa": item.get('company_name'),
                    "cidade": item.get('location', 'Brasil'),
                    "uf": "BR",
                    "tipo": "A combinar",
                    "salario": 0,
                    "nivel": "Google Jobs",
                    "fonte": "Google",
                    "link": item.get('share_link', '#')
                })
    except: pass

    return pd.DataFrame(lista_final)

# --- INTERFACE ---
def main():
    st.title("💼 Portal Nacional de Oportunidades")
    st.markdown("### Conectando você às melhores vagas em todo o Brasil")
    
    st.sidebar.header("📡 Status de Conexão")
    df_vagas = carregar_vagas_integradas()

    if df_vagas.empty:
        st.warning("Sincronizando base nacional... Por favor, aguarde.")
        return

    # --- FILTROS LATERAIS ---
    st.sidebar.divider()
    st.sidebar.header("🔍 Filtros de Busca")
    busca = st.sidebar.text_input("Cargo, Empresa ou Palavra-chave:")
    
    # Extrair UFs de forma limpa
    lista_ufs = sorted(list(set([str(uf).strip().upper() for uf in df_vagas['uf'].unique() if pd.notna(uf)])))
    uf_sel = st.sidebar.selectbox("Estado (UF):", ["Brasil (Todos)"] + lista_ufs)
    
    tipo_sel = st.sidebar.selectbox("Modalidade:", ["Todas"] + list(df_vagas['tipo'].unique()))

    # Lógica de Filtro
    df_f = df_vagas.copy()
    if busca: 
        df_f = df_f[df_f['titulo'].str.contains(busca, case=False, na=False) | 
                    df_f['empresa'].str.contains(busca, case=False, na=False)]
    if uf_sel != "Brasil (Todos)": 
        df_f = df_f[df_f['uf'] == uf_sel]
    if tipo_sel != "Todas": 
        df_f = df_f[df_f['tipo'] == tipo_sel]

    st.write(f"Exibindo **{len(df_f)}** oportunidades encontradas hoje.")

    # Exibição dos Cards
    for i, vaga in df_f.iterrows():
        try:
            sal = float(vaga['salario'])
            texto_salario = f"R$ {sal:,.2f}" if sal > 0 else "A combinar"
        except:
            texto_salario = "A combinar"

        st.markdown(f"""
            <div class="vaga-card">
                <div class="titulo-vaga">{vaga['titulo']}</div>
                <div class="empresa-vaga">🏢 {vaga['empresa']}</div>
                <div>
                    <span class="tag tag-local">📍 {vaga['cidade']} - {vaga['uf']}</span>
                    <span class="tag tag-tipo">💻 {vaga['tipo']}</span>
                    <span class="tag tag-fonte">🔗 Fonte: {vaga['fonte']}</span>
                </div>
                <div class="valor-vaga">💰 {texto_salario}</div>
            </div>
        """, unsafe_allow_html=True)
        st.link_button(f"🚀 Candidatar-se na {vaga['fonte']}", vaga['link'], key=f"btn_{i}")
        st.write("")

if __name__ == "__main__":
    main()
