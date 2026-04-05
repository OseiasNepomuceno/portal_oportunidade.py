import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from streamlit_gsheets import GSheetsConnection

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

# --- FUNÇÃO DE CARREGAMENTO (AGORA APENAS PLANILHA) ---

@st.cache_data(ttl=600)
def carregar_vagas_acumuladas():
    try:
        # Conecta apenas à planilha que o seu minerador está alimentando
        conn = st.connection("gsheets", type=GSheetsConnection)
        df = conn.read()
        df = df.dropna(how="all")
        
        # Garante que as colunas essenciais existam e filtra apenas ativas
        if not df.empty and 'Status' in df.columns:
            df = df[df['Status'].str.lower() == 'ativa']
            
        return df
    except Exception as e:
        st.error(f"Erro ao conectar com a base de dados: {e}")
        return pd.DataFrame()

# --- INTERFACE ---
def main():
    st.title("💼 Portal Nacional de Oportunidades")
    
    # Agora o portal lê o histórico acumulado pelo minerador
    df_vagas = carregar_vagas_acumuladas()

    if df_vagas.empty:
        st.info("Estamos atualizando nossa base com novas oportunidades. Volte em instantes!")
        return

    # --- LÓGICA DE MÉTRICAS REAIS ---
    total_vagas = len(df_vagas)
    
    # Calcula vagas captadas nas últimas 24h (se a coluna Data_Captura existir)
    vagas_hoje = 0
    if 'Data_Captura' in df_vagas.columns:
        try:
            hoje_str = datetime.now().strftime("%Y-%m-%d")
            vagas_hoje = len(df_vagas[df_vagas['Data_Captura'] == hoje_str])
        except:
            vagas_hoje = 30 # fallback caso a data falte

    col_m1, col_m2, col_m3 = st.columns([1, 1, 1.5])
    
    with col_m1:
        st.metric("Oportunidades Ativas", f"{total_vagas}")
    with col_m2:
        st.metric("Captadas Hoje", f"+{vagas_hoje}", delta_color="normal")
    with col_m3:
        st.markdown(f"""
            <div style="background-color: #e8f5e9; padding: 10px; border-radius: 10px; border: 1px solid #c8e6c9;">
                <p style="margin:0; color: #2e7d32; font-weight: bold;">📢 Compartilhe e ajude um amigo!</p>
                <a href="https://wa.me/?text=Encontrei%20mais%20de%20{total_vagas}%20vagas%20no%20Portal%20Nacional%20de%20Oportunidades!%20Confira%20aqui:" target="_blank" style="text-decoration:none; color: #1b5e20; font-size: 14px;">👉 Enviar para o WhatsApp</a>
            </div>
        """, unsafe_allow_html=True)

    st.markdown(f"""
        <div class="metric-container">
            <h4 style="margin:0; color: #0d47a1;">🚀 Uma dessas {total_vagas} vagas pode ser a sua!</h4>
            <p style="margin:5px 0 0 0; color: #1565c0;">Mantemos um histórico de 30 dias de oportunidades para você não perder nada.</p>
        </div>
    """, unsafe_allow_html=True)

    # --- FILTROS LATERAIS ---
    st.sidebar.header("🔍 Filtros de Busca")
    busca = st.sidebar.text_input("Cargo, Empresa ou Palavra-chave:")
    
    # Filtro de UF dinâmico
    uf_lista = ["Brasil (Todos)"]
    if 'UF' in df_vagas.columns:
        ufs = sorted(list(set([str(u).strip().upper() for u in df_vagas['UF'].unique() if pd.notna(u) and len(str(u)) <= 2])))
        uf_lista += ufs
    
    uf_sel = st.sidebar.selectbox("Estado (UF):", uf_lista)
    
    tipo_sel = "Todas"
    if 'Tipo' in df_vagas.columns:
        tipos = ["Todas"] + sorted(list(df_vagas['Tipo'].unique()))
        tipo_sel = st.sidebar.selectbox("Modalidade:", tipos)

    st.sidebar.divider()
    st.sidebar.info("Aumentamos nosso banco de dados! Agora você visualiza vagas acumuladas dos últimos 30 dias.")

    # --- LÓGICA DE FILTRO ---
    df_f = df_vagas.copy()
    if busca: 
        df_f = df_f[df_f['Título'].str.contains(busca, case=False, na=False) | 
                    df_f['Empresa'].str.contains(busca, case=False, na=False)]
    if uf_sel != "Brasil (Todos)": 
        df_f = df_f[df_f['UF'] == uf_sel]
    if tipo_sel != "Todas": 
        df_f = df_f[df_f['Tipo'] == tipo_sel]

    st.write(f"Exibindo **{len(df_f)}** resultados.")

    # --- EXIBIÇÃO DOS CARDS ---
    for i, vaga in df_f.iterrows():
        try:
            # Tratamento de salário (Adzuna traz números, Google traz texto)
            sal = vaga.get('Salário', 0)
            texto_salario = f"R$ {float(sal):,.2f}" if float(sal) > 0 else "A combinar"
        except:
            texto_salario = "A combinar"

        st.markdown(f"""
            <div class="vaga-card">
                <div class="titulo-vaga">{vaga.get('Título', 'Vaga')}</div>
                <div class="empresa-vaga">🏢 {vaga.get('Empresa', 'Confidencial')}</div>
                <div>
                    <span class="tag tag-local">📍 {vaga.get('Cidade', 'Brasil')} - {vaga.get('UF', 'BR')}</span>
                    <span class="tag tag-tipo">💻 {vaga.get('Tipo', 'Presencial')}</span>
                    <span class="tag tag-fonte">🔗 {vaga.get('Fonte', 'Portal')}</span>
                </div>
                <div class="valor-vaga">💰 {texto_salario}</div>
            </div>
        """, unsafe_allow_html=True)
        st.link_button(f"🚀 Ver detalhes e Candidatar-se", vaga.get('Link_Inscrição', '#'), key=f"btn_{i}")
        st.write("")

if __name__ == "__main__":
    main()
