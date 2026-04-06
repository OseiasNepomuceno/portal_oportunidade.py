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
    
    .metric-container {
        background-color: #e3f2fd;
        padding: 20px;
        border-radius: 15px;
        border-left: 5px solid #2196f3;
        margin-bottom: 25px;
    }
    </style>
""", unsafe_allow_html=True)

# --- FUNÇÃO DA IA (ATUALIZADA COM MODELO LLAMA 3.1) ---
def estruturar_curriculo_ia(texto_antigo, novas_infos, vaga_objetivo="Geral"):
    try:
        # 1. Recupera a chave da Groq nos Secrets
        api_key = st.secrets.get("GROQ_API_KEY")
        if not api_key:
            return "Erro: Chave GROQ_API_KEY não configurada nos Secrets do Streamlit."
            
        client = Groq(api_key=api_key)
        
        prompt = f"""
        Atue como um Especialista em Recrutamento sênior, mestre nos frameworks STAR, WHO e ELITE.
        TAREFA: Reescrever as experiências profissionais abaixo focando em resultados numéricos e verbos de ação.
        
        DADOS ATUAIS: {texto_antigo}
        ATUALIZAÇÕES: {novas_infos}
        VAGA ALVO: {vaga_objetivo}
        
        REGRAS: 
        - Use tópicos, negrito e linguagem profissional de alto impacto. 
        - Retorne apenas o texto reestruturado do currículo.
        """
        
        # Chamada ao modelo Llama 3.1 (Atualizado para evitar erro de descontinuação)
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=2048,
        )
        
        return completion.choices[0].message.content
    except Exception as e:
        return f"Erro técnico na Groq: {str(e)}"

# --- FUNÇÃO DE CARREGAMENTO ---
@st.cache_data(ttl=0) 
def carregar_vagas_acumuladas():
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        df = conn.read()
        df = df.dropna(how="all")
        if not df.empty and 'Status' in df.columns:
            df = df[df['Status'].str.lower() == 'ativa']
        return df
    except Exception as e:
        st.error(f"Erro ao conectar com a base de dados: {e}")
        return pd.DataFrame()

# --- INTERFACE PRINCIPAL ---
def main():
    if 'cv_preview' not in st.session_state:
        st.session_state.cv_preview = ""

    st.title("💼 Portal Nacional de Oportunidades")
    
    df_vagas = carregar_vagas_acumuladas()

    if df_vagas.empty:
        st.info("Estamos atualizando nossa base com novas oportunidades. Volte em instantes!")
        return

    # --- MÉTRICAS ---
    total_vagas = len(df_vagas)
    vagas_hoje = 0
    if 'Data_Captura' in df_vagas.columns:
        try:
            hoje_str = datetime.now().strftime("%Y-%m-%d")
            vagas_hoje = len(df_vagas[df_vagas['Data_Captura'] == hoje_str])
        except:
            vagas_hoje = 0

    url_do_
