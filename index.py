import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from streamlit_gsheets import GSheetsConnection
import urllib.parse
import google.generativeai as genai # Importação da IA

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Portal Nacional de Oportunidades", page_icon="💼", layout="wide")

# --- CONFIGURAÇÃO DA IA ---
# Certifique-se de adicionar GEMINI_API_KEY aos segredos do Streamlit
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except:
    pass # Caso ainda não tenha configurado o Secret, o app não quebra

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

# --- FUNÇÃO DA IA (PASSO 3 - LÓGICA) ---
def estruturar_curriculo_ia(texto_antigo, novas_infos, vaga_objetivo="Geral"):
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = f"""
        Atue como um Especialista em Recrutamento e Seleção sênior, mestre nos frameworks STAR, WHO e ELITE.
        TAREFA: Reescrever as experiências profissionais e educacionais baseando-se nos dados abaixo.
        
        DADOS DO CURRÍCULO ATUAL: {texto_antigo}
        NOVAS ATUALIZAÇÕES: {novas_infos}
        VAGA DE INTERESSE: {vaga_objetivo}
        
        REGRAS:
        1. Framework STAR: Foco em Ação e Resultado (números, %).
        2. Verbos de Ação: Inicie com verbos fortes (Otimizei, Desenvolvi).
        3. Formate a saída de forma limpa e profissional.
        """
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Erro ao processar com IA: {e}"

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

    url_do_site = "https://oportunidade.streamlit.app/" 
    texto_share = f"🚀 Encontrei {total_vagas} vagas ativas no Portal Nacional de Oportunidades! Confira aqui: {url_do_site}"
    link_wa = f"https://wa.me/?text={urllib.parse.quote(texto_share)}"

    col_m1, col_m2, col_m3 = st.columns([1, 1, 1.5])
    with col_m1:
        st.metric("Oportunidades Ativas", f"{total_vagas}")
    with col_m2:
        st.metric("Captadas Hoje", f"+{vagas_hoje}")
    with col_m3:
        st.markdown(f"""
            <div style="background-color: #e8f5e9; padding: 10px; border-radius: 10px; border: 1px solid #c8e6c9;">
                <p style="margin:0; color: #2e7d32; font-weight: bold;">📢 Compartilhe e ajude um amigo!</p>
                <a href="{link_wa}" target="_blank" style="text-decoration:none; color: #1b5e20; font-size: 14px; font-weight: bold;">👉 Enviar para o WhatsApp</a>
            </div>
        """, unsafe_allow_html=True)

    st.markdown(f"""
        <div class="metric-container">
            <h4 style="margin:0; color: #0d47a1;">🚀 Uma dessas {total_vagas} vagas pode ser a sua!</h4>
        </div>
    """, unsafe_allow_html=True)

    # --- PASSO 3: INTERFACE DA IA DE CURRÍCULO ---
    st.divider()
    st.subheader("✨ Upgrade de Currículo com IA")
    with st.expander("Clique aqui para atualizar seu currículo com Frameworks Avançados (STAR/WHO)"):
        st.write("Transforme seu currículo comum em um perfil focado em resultados.")
        
        col_cv1, col_cv2 = st.columns(2)
        with col_cv1:
            curriculo_texto = st.text_area("Cole seu currículo atual aqui:", height=200)
        with col_cv2:
            novas_insercoes = st.text_area("Novas informações (Cursos, Promoções, Conquistas):", height=200)
        
        vaga_alvo = st.text_input("Cargo ou link da vaga que deseja conquistar:")

        if st.button("🚀 Gerar Prévia do Novo Currículo"):
            if curriculo_texto:
                with st.spinner("Nossa IA está reestruturando sua carreira..."):
                    texto_final = estruturar_curriculo_ia(curriculo_texto, novas_insercoes, vaga_alvo)
                    st.markdown("### 📝 Sua Experiência Reestruturada:")
                    st.info(texto_final)
                    
                    st.success("✅ Texto gerado com sucesso!")
                    st.warning("💳 Deseja baixar o PDF formatado profissionalmente?")
                    st.link_button("💳 Pagar R$ 29,90 e Gerar PDF Profissional", "https://link-do-seu-checkout.com")
            else:
                st.error("Por favor, cole seu currículo atual para começar.")
    st.divider()

    # --- FILTROS ---
    st.sidebar.header("🔍 Filtros de Busca")
    busca = st.sidebar.text_input("Cargo ou Empresa:")
    
    uf_lista = ["Brasil (Todos)"]
    if 'UF' in df_vagas.columns:
        ufs = sorted(list(set([str(u).strip().upper() for u in df_vagas['UF'].unique() if pd.notna(u)])))
        uf_lista += ufs
    
    uf_sel = st.sidebar.selectbox("Estado (UF):", uf_lista)
    
    tipo_sel = "Todas"
    if 'Tipo' in df_vagas.columns:
        tipos = ["Todas"] + sorted(list(df_vagas['Tipo'].unique()))
        tipo_sel = st.sidebar.selectbox("Modalidade:", tipos)

    # --- APLICAÇÃO DOS FILTROS ---
    df_f = df_vagas.copy()
    if busca: 
        df_f = df_f[df_f['Título'].str.contains(busca, case=False, na=False) | 
                    df_f['Empresa'].str.contains(busca, case=False, na=False)]
    if uf_sel != "Brasil (Todos)": 
        df_f = df_f[df_f['UF'] == uf_sel]
    if tipo_sel != "Todas": 
        df_f = df_f[df_f['Tipo'] == tipo_sel]

    st.write(f"Exibindo **{len(df_f)}** resultados.")

    # --- RENDERIZAÇÃO DAS VAGAS ---
    for i, vaga in df_f.iterrows():
        try:
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
