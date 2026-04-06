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

# --- FUNÇÃO DA IA (GERAÇÃO DE CURRÍCULO E CARTA) ---
def gerar_combo_carreira_ia(texto_antigo, novas_infos, vaga_objetivo="Geral"):
    try:
        api_key = st.secrets.get("GROQ_API_KEY")
        if not api_key:
            return None, "Erro: Chave API não configurada."
            
        client = Groq(api_key=api_key)
        
        prompt = f"""
        Atue como um Especialista em Recrutamento sênior.
        TAREFA: Gere dois documentos baseados nos dados abaixo.
        
        DADOS DO CANDIDATO: {texto_antigo}
        ATUALIZAÇÕES: {novas_infos}
        OBJETIVO: {vaga_objetivo}
        
        1. CURRÍCULO: Reestruturado com STAR/WHO, foco em resultados e verbos de ação.
        2. CARTA DE APRESENTAÇÃO: Persuasiva, profissional e alinhada ao objetivo.
        
        REGRAS: 
        - Separe os documentos com a tag [DIVISOR].
        - Use linguagem de alto impacto.
        - Retorne apenas o conteúdo dos documentos.
        """
        
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=3000,
        )
        
        resposta = completion.choices[0].message.content
        if "[DIVISOR]" in resposta:
            cv, carta = resposta.split("[DIVISOR]")
            return cv.strip(), carta.strip()
        return resposta, "Carta gerada automaticamente no PDF final."
        
    except Exception as e:
        return None, f"Erro técnico: {str(e)}"

# --- CARREGAMENTO DE DADOS ---
@st.cache_data(ttl=0) 
def carregar_vagas():
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        df = conn.read().dropna(how="all")
        if 'Status' in df.columns:
            df = df[df['Status'].str.lower() == 'ativa']
        return df
    except:
        return pd.DataFrame()

# --- INTERFACE ---
def main():
    if 'cv_data' not in st.session_state: st.session_state.cv_data = None
    if 'carta_data' not in st.session_state: st.session_state.carta_data = None

    st.title("💼 Portal Nacional de Oportunidades")
    df_vagas = carregar_vagas()

    # --- SEÇÃO IA ---
    st.divider()
    st.subheader("✨ Combo Profissional: Currículo + Carta de Apresentação")
    with st.expander("Clique aqui para turbinar sua candidatura", expanded=True):
        col_cv1, col_cv2 = st.columns(2)
        with col_cv1:
            curriculo_texto = st.text_area("Cole seu currículo atual:", height=150, key="txt_antigo")
        with col_cv2:
            novas_insercoes = st.text_area("Novas conquistas/cursos:", height=150, key="txt_novo")
        
        vaga_alvo = st.text_input("Vaga ou cargo desejado:", key="txt_vaga")

        if st.button("🚀 Gerar Documentos Profissionais"):
            if curriculo_texto:
                with st.spinner("⏳ IA preparando seu kit de aprovação..."):
                    cv, carta = gerar_combo_carreira_ia(curriculo_texto, novas_insercoes, vaga_alvo)
                    st.session_state.cv_data = cv
                    st.session_state.carta_data = carta
            else:
                st.error("Por favor, preencha seu currículo atual.")

        if st.session_state.cv_data:
            st.success("✅ Seu Currículo e sua Carta de Apresentação foram gerados com sucesso!")
            st.markdown("""
                **O que está incluso no seu PDF Profissional:**
                * ✅ Currículo otimizado com Frameworks STAR e WHO.
                * ✅ Carta de Apresentação persuasiva para a vaga selecionada.
                * ✅ Formatação pronta para sistemas de recrutamento (ATS).
            """)
            st.link_button("💳 Pagar R$ 29,90 e Receber Kit Completo", "https://mpago.la/2CVmJ4K")

    st.divider()
    
    # --- FILTROS E VAGAS (Mantém sua lógica original abaixo) ---
    st.sidebar.header("🔍 Filtros")
    # ... (restante do seu código de filtros e listagem de vagas) ...

if __name__ == "__main__":
    main()
