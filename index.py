import streamlit as st
import pandas as pd
import requests
import os

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
        transition: transform 0.2s;
    }
    .vaga-card:hover {
        transform: scale(1.01);
        background-color: #ffffff;
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
    .tag-nivel { background-color: #fff3e0; color: #e65100; }
    .tag-fonte { background-color: #f3e5f5; color: #4a148c; border: 1px solid #ce93d8; }
    .valor-vaga { color: #2e7d32; font-weight: bold; font-size: 16px; margin-top: 10px; }
    </style>
""", unsafe_allow_html=True)

# --- FUNÇÕES DE CAPTAÇÃO DE DADOS ---

@st.cache_data(ttl=600) # Atualiza a cada 10 min
def carregar_dados_integrados():
    # 1. GOOGLE SHEETS (Dados Práticos)
    # Requer configuração em .streamlit/secrets.toml
    try:
        from streamlit_gsheets import GSheetsConnection
        conn = st.connection("gsheets", type=GSheetsConnection)
        df_sheets = conn.read(ttl="10m")
        df_sheets['fonte'] = 'CoreGov (Planilha)'
    except:
        df_sheets = pd.DataFrame()

    # 2. ADZUNA API (Vagas Reais Automáticas)
    # Nota: Substitua APP_ID e APP_KEY pelos seus da Adzuna
    APP_ID = st.secrets.get("ADZUNA_ID", "seu_id")
    APP_KEY = st.secrets.get("ADZUNA_KEY", "sua_key")
    vagas_api = []
    
    try:
        url = f"https://api.adzuna.com/v1/api/jobs/br/search/1?app_id={APP_ID}&app_key={APP_KEY}&results_per_page=10&what=administrativo"
        response = requests.get(url).json()
        for item in response.get('results', []):
            vagas_api.append({
                "titulo": item.get('title'),
                "empresa": item.get('company', {}).get('display_name'),
                "cidade": item.get('location', {}).get('display_name'),
                "uf": "BR",
                "tipo": "Remoto" if "remoto" in item.get('description').lower() else "Presencial",
                "salario": item.get('salary_min', 0),
                "nivel": "Não informado",
                "fonte": "Adzuna API",
                "link": item.get('redirect_url')
            })
    except:
        pass

    df_api = pd.DataFrame(vagas_api)
    
    # 3. WEB SCRAPING / MANUAL FALLBACK
    vagas_scraping = [
        {"titulo": "Analista de Projetos Automação", "empresa": "LinkedIn Scraping", "cidade": "Frutal", "uf": "MG", "tipo": "Híbrido", "salario": 6000.00, "nivel": "Sênior", "fonte": "Automação Web", "link": "#"}
    ]
    df_scrap = pd.DataFrame(vagas_scraping)

    # UNIFICANDO TUDO
    df_final = pd.concat([df_sheets, df_api, df_scrap], ignore_index=True)
    return df_final

# --- INTERFACE PRINCIPAL ---
def main():
    st.title("💼 Portal de Oportunidades CoreGov")
    st.caption("Central de Inteligência em Recrutamento | Oseias 2026")

    df_vagas = carregar_dados_integrados()

    # --- SIDEBAR: FILTROS ESTRATÉGICOS ---
    with st.sidebar:
        st.header("🎯 Filtros Estratégicos")
        
        busca = st.text_input("🔍 Cargo ou Palavra-chave:")
        
        # Filtro de Localização (UF)
        ufs = ["Todos"] + sorted([x for x in df_vagas['uf'].unique() if pd.notna(x)])
        uf_sel = st.selectbox("📍 Localização (UF):", ufs)
        
        # Filtro de Modalidade
        modalidades = ["Todas"] + list(df_vagas['tipo'].unique())
        tipo_sel = st.selectbox("💻 Modalidade:", modalidades)
        
        # Filtro de Nível
        niveis = ["Todos", "Estágio", "Júnior", "Pleno", "Sênior", "Especialista"]
        nivel_sel = st.selectbox("📊 Nível de Experiência:", niveis)

        st.divider()
        st.write("✨ **Fontes Ativas:**")
        st.checkbox("Planilha Google", value=True, disabled=True)
        st.checkbox("API Adzuna", value=True, disabled=True)
        st.checkbox("LinkedIn Scraping", value=True, disabled=True)

    # --- LÓGICA DE FILTRAGEM ---
    df_f = df_vagas.copy()
    if busca:
        df_f = df_f[df_f['titulo'].str.contains(busca, case=False, na=False)]
    if uf_sel != "Todos":
        df_f = df_f[df_f['uf'] == uf_sel]
    if tipo_sel != "Todas":
        df_f = df_f[df_f['tipo'] == tipo_sel]
    if nivel_sel != "Todos":
        df_f = df_f[df_f['nivel'] == nivel_sel]

    st.write(f"Encontradas **{len(df_f)}** oportunidades para você:")

    # --- EXIBIÇÃO DOS CARDS ---
    for i, vaga in df_f.iterrows():
        # Lógica de Ícones
        icon_tipo = "🏠" if vaga['tipo'] == "Remoto" else "🏢"
        
        st.markdown(f"""
            <div class="vaga-card">
                <div class="titulo-vaga">{vaga['titulo']}</div>
                <div class="empresa-vaga">💼 {vaga['empresa']}</div>
                <div>
                    <span class="tag tag-local">📍 {vaga['cidade']} - {vaga['uf']}</span>
                    <span class="tag tag-tipo">{icon_tipo} {vaga['tipo']}</span>
                    <span class="tag tag-nivel">📊 {vaga.get('nivel', 'Nível não informado')}</span>
                    <span class="tag tag-fonte">🔗 Fonte: {vaga['fonte']}</span>
                </div>
                <div class="valor-vaga">💰 R$ {float(vaga['salario']):,.2f}</div>
            </div>
        """, unsafe_allow_html=True)
        
        col_btn, _ = st.columns([1, 5])
        with col_btn:
            st.link_button("🚀 Candidatar-se", vaga.get('link', '#'), use_container_width=True)
        st.write("")

if __name__ == "__main__":
    main()
