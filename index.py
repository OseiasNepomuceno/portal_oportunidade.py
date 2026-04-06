import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection
import urllib.parse
from groq import Groq 

# --- CONFIGURAÇÃO DA PÁGINA ---
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

# --- FUNÇÃO DA IA ---
def gerar_combo_carreira_ia(texto_antigo, novas_infos, vaga_objetivo="Geral"):
    try:
        api_key = st.secrets.get("GROQ_API_KEY")
        if not api_key: return None, "Erro: Chave API não configurada."
        client = Groq(api_key=api_key)
        prompt = f"Gere Currículo e Carta de Apresentação para: {texto_antigo}. Novas infos: {novas_infos}. Vaga: {vaga_objetivo}. Separe por [DIVISOR]."
        completion = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role": "user", "content": prompt}], temperature=0.7)
        resposta = completion.choices[0].message.content
        if "[DIVISOR]" in resposta:
            parts = resposta.split("[DIVISOR]")
            return parts[0].strip(), parts[1].strip()
        return resposta, "Carta gerada com sucesso."
    except Exception as e: return None, f"Erro: {str(e)}"

# --- FUNÇÃO DE CARREGAMENTO ---
@st.cache_data(ttl=0) 
def carregar_vagas_acumuladas():
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        df = conn.read().dropna(how="all")
        if not df.empty and 'Status' in df.columns:
            df = df[df['Status'].str.lower() == 'ativa']
        return df
    except: return pd.DataFrame()

# --- INTERFACE PRINCIPAL ---
def main():
    # --- LOGOTIPO ---
    try:
        st.sidebar.image("Logo Portal Nacional de Oportunidade.png", use_container_width=True)
    except: pass

    if 'cv_data' not in st.session_state: st.session_state.cv_data = None
    if 'carta_data' not in st.session_state: st.session_state.carta_data = None

    st.title("💼 Portal Nacional de Oportunidades")
    df_vagas = carregar_vagas_acumuladas()

    if df_vagas.empty:
        st.info("Estamos atualizando nossa base. Volte em instantes!")
    else:
        # --- MÉTRICAS ---
        total_vagas = len(df_vagas)
        hoje_str = datetime.now().strftime("%Y-%m-%d")
        vagas_hoje = len(df_vagas[df_vagas['Data_Captura'] == hoje_str]) if 'Data_Captura' in df_vagas.columns else 0

        col_m1, col_m2, col_m3 = st.columns([1, 1, 1.5])
        with col_m1: st.metric("Oportunidades Ativas", f"{total_vagas}")
        with col_m2: st.metric("Captadas Hoje", f"+{vagas_hoje}")
        with col_m3:
            url_site = "https://oportunidade.streamlit.app/"
            link_wa = f"https://wa.me/?text={urllib.parse.quote(f'🚀 Encontrei {total_vagas} vagas! {url_site}')}"
            st.markdown(f'<div style="background-color:#e8f5e9;padding:10px;border-radius:10px;border:1px solid #c8e6c9;"><a href="{link_wa}" target="_blank" style="text-decoration:none;color:#2e7d32;font-weight:bold;">📢 Compartilhar no WhatsApp</a></div>', unsafe_allow_html=True)

        # --- IA COMBO ---
        st.divider()
        with st.expander("✨ Combo Profissional: Currículo + Carta com IA", expanded=False):
            c1, c2 = st.columns(2)
            curriculo_texto = c1.text_area("Currículo atual:", height=100)
            novas_infos = c2.text_area("Novas experiências:", height=100)
            vaga_alvo = st.text_input("Vaga alvo:")
            if st.button("🚀 Gerar Kit Profissional"):
                if curriculo_texto:
                    with st.spinner("Gerando..."):
                        cv, carta = gerar_combo_carreira_ia(curriculo_texto, novas_infos, vaga_alvo)
                        st.session_state.cv_data, st.session_state.carta_data = cv, carta
                else: st.error("Cole seu currículo.")
            if st.session_state.cv_data:
                st.success("✅ Kit Profissional Pronto!")
                st.link_button("💳 Pagar R$ 29,90 e Baixar", "https://mpago.la/2CVmJ4K")

        # --- SIDEBAR: FILTROS E RESUMO ---
        st.sidebar.header("🔍 Filtros de Busca")
        busca = st.sidebar.text_input("Cargo ou Empresa:")
        
        # Filtro de UF
        uf_lista = ["Brasil (Todos)"] + sorted([str(u).upper() for u in df_vagas['UF'].unique() if pd.notna(u)])
        uf_sel = st.sidebar.selectbox("Estado (UF):", uf_lista)

        # Filtro de Cidade (Dinâmico)
        cidade_lista = ["Todas as Cidades"]
        if uf_sel != "Brasil (Todos)":
            cidades_uf = df_vagas[df_vagas['UF'] == uf_sel]['Cidade'].unique()
            cidade_lista += sorted([str(c) for c in cidades_uf if pd.notna(c)])
        cidade_sel = st.sidebar.selectbox("Cidade:", cidade_lista)

        tipo_sel = st.sidebar.selectbox("Modalidade:", ["Todas"] + sorted(list(df_vagas['Tipo'].unique())))

        # --- NOVIDADE: RESUMO POR ESTADO ---
        st.sidebar.divider()
        with st.sidebar.expander("📊 Vagas por Estado"):
            vagas_por_uf = df_vagas['UF'].value_counts().sort_index()
            for uf, qtd in vagas_por_uf.items():
                if st.button(f"{uf}: {qtd} vagas", key=f"btn_uf_{uf}"):
                    # Aqui o botão funciona como um atalho para o filtro de UF
                    st.rerun() # Opcional: apenas para atualizar a UI se necessário

        # --- LÓGICA DE FILTRAGEM ---
        df_f = df_vagas.copy()
        if busca: df_f = df_f[df_f['Título'].str.contains(busca, case=False) | df_f['Empresa'].str.contains(busca, case=False)]
        if uf_sel != "Brasil (Todos)": df_f = df_f[df_f['UF'] == uf_sel]
        if cidade_sel != "Todas as Cidades": df_f = df_f[df_f['Cidade'] == cidade_sel]
        if tipo_sel != "Todas": df_f = df_f[df_f['Tipo'] == tipo_sel]

        st.subheader(f"📍 {len(df_f)} Oportunidades encontradas")

        # --- LISTAGEM ---
        for i, vaga in df_f.iterrows():
            st.markdown(f"""
                <div class="vaga-card">
                    <div class="titulo-vaga">{vaga.get('Título', 'Vaga')}</div>
                    <div class="empresa-vaga">🏢 {vaga.get('Empresa', 'Confidencial')}</div>
                    <div>
                        <span class="tag tag-local">📍 {vaga.get('Cidade', 'Brasil')} - {vaga.get('UF', 'BR')}</span>
                        <span class="tag tag-tipo">💻 {vaga.get('Tipo', 'Presencial')}</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            st.link_button(f"🚀 Ver detalhes", vaga.get('Link_Inscrição', '#'), key=f"v_{i}")

if __name__ == "__main__":
    main()
