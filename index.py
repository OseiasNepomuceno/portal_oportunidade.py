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

    # 1. GOOGLE SHEETS (Vinculando com suas colunas reais)
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        df_sheets = conn.read()
        df_sheets = df_sheets.dropna(how="all")
        
        # Mapeamento: Pegamos o nome da sua planilha e convertemos para o padrão do site
        for _, row in df_sheets.iterrows():
            # Só adiciona se a vaga estiver com Status 'Ativa' ou se não houver coluna status
            if str(row.get('Status', '')).lower() == 'inativa':
                continue
                
            lista_final.append({
                "titulo": str(row.get('Título', 'Vaga Sem Título')),
                "empresa": str(row.get('Empresa', 'CoreGov')),
                "cidade": str(row.get('Cidade', 'Brasil')),
                "uf": str(row.get('UF', 'BR')),
                "tipo": str(row.get('Tipo', 'Presencial')),
                "salario": row.get('Salário', 0),
                "nivel": str(row.get('Área', 'Geral')), # Usando 'Área' como nível/categoria
                "fonte": "CoreGov (Interno)",
                "link": str(row.get('Link_Inscrição', '#'))
            })
    except Exception as e:
        st.sidebar.error(f"⚠️ Erro Planilha: {e}")

    # 2. ADZUNA API
    try:
        aid = st.secrets["ADZUNA_ID"]
        akey = st.secrets["ADZUNA_KEY"]
        url_adz = f"https://api.adzuna.com/v1/api/jobs/br/search/1?app_id={aid}&app_key={akey}&results_per_page=15&what=administrativo"
        res_adz = requests.get(url_adz).json()
        if 'results' in res_adz:
            for item in res_adz.get('results', []):
                lista_final.append({
                    "titulo": item.get('title'),
                    "empresa": item.get('company', {}).get('display_name', 'Confidencial'),
                    "cidade": item.get('location', {}).get('display_name', 'Remoto'),
                    "uf": "BR",
                    "tipo": "Remoto" if "remoto" in item.get('description', '').lower() else "Presencial",
                    "salario": item.get('salary_min', 0),
                    "nivel": "Mercado",
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
        if 'jobs' in res_jooble:
            for item in res_jooble.get('jobs', []):
                lista_final.append({
                    "titulo": item.get('title'),
                    "empresa": item.get('company', 'Confidencial'),
                    "cidade": item.get('location', 'Brasil'),
                    "uf": "BR",
                    "tipo": "Híbrido",
                    "salario": 0,
                    "nivel": "Mercado",
                    "fonte": "Jooble",
                    "link": item.get('link')
                })
    except:
        pass

    return pd.DataFrame(lista_final)

# --- INTERFACE ---
def main():
    st.title("💼 Portal de Oportunidades CoreGov")
    st.sidebar.header("📡 Status de Conexão")
    
    df_vagas = carregar_vagas_integradas()

    if df_vagas.empty:
        st.warning("Sincronizando base de dados... Por favor, aguarde.")
        return

    # --- FILTROS LATERAIS ---
    st.sidebar.divider()
    st.sidebar.header("🔍 Filtros")
    busca = st.sidebar.text_input("Cargo ou Área:")
    
    lista_ufs = sorted([str(uf) for uf in df_vagas['uf'].unique() if pd.notna(uf)])
    uf_sel = st.sidebar.selectbox("Estado:", ["Todos"] + lista_ufs)
    
    lista_tipos = [str(tipo) for tipo in df_vagas['tipo'].unique() if pd.notna(tipo)]
    tipo_sel = st.sidebar.selectbox("Modalidade:", ["Todas"] + lista_tipos)

    # Lógica de Filtro
    df_f = df_vagas.copy()
    if busca: 
        df_f = df_f[df_f['titulo'].str.contains(busca, case=False, na=False) | df_f['nivel'].str.contains(busca, case=False, na=False)]
    if uf_sel != "Todos": 
        df_f = df_f[df_f['uf'] == uf_sel]
    if tipo_sel != "Todas": 
        df_f = df_f[df_f['tipo'] == tipo_sel]

    st.write(f"Encontradas **{len(df_f)}** oportunidades.")

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
        st.link_button(f"🚀 Ver detalhes e Candidatar-se", vaga['link'], key=f"btn_{i}")
        st.write("")

if __name__ == "__main__":
    main()
