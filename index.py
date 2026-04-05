import streamlit as st
import pandas as pd
import requests
import os
from streamlit_gsheets import GSheetsConnection

# Configuração da Página
st.set_page_config(page_title="Portal de Oportunidades | CoreGov", page_icon="💼", layout="wide")

# --- ESTILIZAÇÃO CUSTOMIZADA (CSS) ---
st.markdown("""
    <style>
    .vaga-card {
        background-color: #f8f9fa;
        padding: 25px;
        border-radius: 15px;
        border-left: 8px solid #007bff;
        box-shadow: 3px 3px 10px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    .titulo-vaga { color: #007bff; font-size: 22px; font-weight: bold; margin-bottom: 5px; }
    .empresa-vaga { color: #333; font-size: 18px; font-weight: 500; margin-bottom: 10px; }
    .tag {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: bold;
        margin-right: 8px;
        margin-bottom: 5px;
    }
    .tag-local { background-color: #e1f5fe; color: #01579b; }
    .tag-tipo { background-color: #e8f5e9; color: #1b5e20; }
    .tag-fonte { background-color: #f3e5f5; color: #4a148c; border: 1px solid #ce93d8; }
    .valor-vaga { color: #2e7d32; font-weight: bold; font-size: 16px; margin-top: 10px; }
    </style>
""", unsafe_allow_html=True)

# --- FUNÇÕES DE CAPTAÇÃO DE DADOS ---

@st.cache_data(ttl=600)
def carregar_vagas_integradas():
    lista_final = []

    # 1. GOOGLE SHEETS
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        df_sheets = conn.read()
        df_sheets = df_sheets.dropna(how="all")
        for _, row in df_sheets.iterrows():
            lista_final.append({
                "titulo": str(row.get('titulo', 'Vaga Sem Título')),
                "empresa": str(row.get('empresa', 'Empresa Confidencial')),
                "cidade": str(row.get('cidade', 'Brasil')),
                "uf": str(row.get('uf', 'BR')),
                "tipo": str(row.get('tipo', 'Presencial')),
                "salario": row.get('salario', 0),
                "nivel": str(row.get('nivel', 'Nível não informado')),
                "fonte": "CoreGov (Interno)",
                "link": str(row.get('link', '#'))
            })
    except Exception as e:
        st.sidebar.error(f"Erro Planilha: {e}")

    # 2. ADZUNA API
    try:
        aid = st.secrets["ADZUNA_ID"]
        akey = st.secrets["ADZUNA_KEY"]
        url_adz = f"https://api.adzuna.com/v1/api/jobs/br/search/1?app_id={aid}&app_key={akey}&results_per_page=10&what=administrativo"
        res_adz = requests.get(url_adz).json()
        for item in res_adz.get('results', []):
            lista_final.append({
                "titulo": item.get('title'),
                "empresa": item.get('company', {}).get('display_name', 'Confidencial'),
                "cidade": item.get('location', {}).get('display_name', 'Remoto'),
                "uf": "BR",
                "tipo": "Remoto" if "remoto" in item.get('description', '').lower() else "Presencial",
                "salario": item.get('salary_min', 0),
                "nivel": "Pleno",
                "fonte": "Adzuna",
                "link": item.get('redirect_url')
            })
    except:
        pass

    # 3. JOOBLE API
    try:
        jkey = st.secrets["JOOBLE_KEY"]
        url_jooble = f"https://br.jooble.org/api/{jkey}"
        body = {"keywords": "administrativo", "location": "Brasil"}
        res_jooble = requests.post(url_jooble, json=body).json()
        for item in res_jooble.get('jobs', []):
            lista_final.append({
                "titulo": item.get('title'),
                "empresa": item.get('company', 'Confidencial'),
                "cidade": item.get('location', 'Brasil'),
                "uf": "BR",
                "tipo": "Híbrido",
                "salario": 0,
                "nivel": "Não informado",
                "fonte": "Jooble",
                "link": item.get('link')
            })
    except:
        pass

    return pd.DataFrame(lista_final)

# --- INTERFACE ---
def main():
    st.title("💼 Portal de Oportunidades CoreGov")
    
    df_vagas = carregar_vagas_integradas()

    if df_vagas.empty:
        st.warning("Estamos sincronizando as vagas. Tente novamente em instantes.")
        return

    # --- FILTROS LATERAIS ---
    with st.sidebar:
        st.header("🔍 Filtros")
        busca = st.text_input("Cargo:")
        uf_sel = st.selectbox("Estado:", ["Todos"] + sorted(list(df_vagas['uf'].unique())))
        tipo_sel = st.selectbox("Modalidade:", ["Todas"] + list(df_vagas['tipo'].unique()))

    # Lógica de Filtro
    df_f = df_vagas.copy()
    if busca: 
        df_f = df_f[df_f['titulo'].str.contains(busca, case=False, na=False)]
    if uf_sel != "Todos": 
        df_f = df_f[df_f['uf'] == uf_sel]
    if tipo_sel != "Todas": 
        df_f = df_f[df_f['tipo'] == tipo_sel]

    st.write(f"Encontradas **{len(df_f)}** vagas disponíveis.")

    # Exibição dos Cards
    for i, vaga in df_f.iterrows():
        try:
            valor_salario = float(vaga['salario'])
        except:
            valor_salario = 0.0

        st.markdown(f"""
            <div class="vaga-card">
                <div class="titulo-vaga">{vaga['titulo']}</div>
                <div class="empresa-vaga">🏢 {vaga['empresa']}</div>
                <div>
                    <span class="tag tag-local">📍 {vaga['cidade']} - {vaga['uf']}</span>
                    <span class="tag tag-tipo">💻 {vaga['tipo']}</span>
                    <span class="tag tag-fonte">🔗 {vaga['fonte']}</span>
                </div>
                <div class="valor-vaga">💰 R$ {valor_salario:,.2f}</div>
            </div>
        """, unsafe_allow_html=True)
        st.link_button(f"🚀 Ver detalhes ({vaga['fonte']})", vaga['link'], key=f"btn_{i}")
        st.write("")

if __name__ == "__main__":
    main()
