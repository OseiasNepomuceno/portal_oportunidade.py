import streamlit as st
import google.generativeai as genai

# --- CONFIGURAÇÃO DA API (Lendo dos Secrets) ---
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-pro')
except:
    st.error("Erro: GEMINI_API_KEY não encontrada nos Secrets do Streamlit.")

# Configuração da Página
st.set_page_config(page_title="Engenharia de Carreira IA", layout="wide", page_icon="🚀")

st.title("🚀 Inteligência de Aprovação: O Currículo Irrecusável")
st.markdown("---")

# --- LÓGICA DE ESTADO ---
if "mostrar_diagnostico" not in st.session_state:
    st.session_state.mostrar_diagnostico = False

# --- CAMADA 1: INPUTS ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("📋 Dados da Oportunidade")
    vaga_link = st.text_area("Descrição da Vaga/Requisitos:", height=150)
    salario = st.number_input("Pretensão Salarial (R$):", min_value=1500, step=500, value=3000)
    graduacao = st.selectbox("Sua Graduação:", ["Ensino Médio", "Técnico", "Graduação", "Pós/MBA", "Mestrado/Doc"])

with col2:
    st.subheader("👤 Seu Perfil Atual")
    exp_possuida = st.multiselect("O que você domina:", 
                                   ["Liderança", "Ferramentas Técnicas", "Gestão de Projetos", "Atendimento", "Vendas", "Dados"])
    cv_atual = st.text_area("Cole seu Currículo Atual:", height=150)

# Lógica Interna
if salario >= 10000:
    plano, preco, metodo_nome, framework = "EXECUTIVE", "R$ 197,00", "Protocolo de ROI Executivo", "ELITE"
elif 5000 <= salario < 10000:
    plano, preco, metodo_nome, framework = "PRO", "R$ 97,00", "Método de Alta Performance", "WHO/CAR"
else:
    plano, preco, metodo_nome, framework = "START", "R$ 47,00", "Engenharia de Impacto Imediato", "STAR"

if st.button("⚡ GERAR DIAGNÓSTICO DE IMPACTO"):
    st.session_state.mostrar_diagnostico = True

# --- CAMADA 2: DIAGNÓSTICO E FORMULÁRIO ---
if st.session_state.mostrar_diagnostico:
    st.markdown("---")
    st.error(f"⚠️ **URGÊNCIA:** Vagas de R$ {salario} exigem um **{metodo_nome}**. Seu modelo atual corre risco de descarte.")
    
    with st.form("form_competencias"):
        st.subheader("🛠️ Provas de Competência")
        c1, c2 = st.columns(2)
        with c1:
            tempo_exp = st.selectbox("Experiência na função:", ["Iniciante", "1-3 anos", "3-5 anos", "5-10 anos", "10+ anos"])
            resultado_impacto = st.text_area("Seu maior resultado real (Números/Metas):")
        with c2:
            ferramentas = st.text_input("Ferramentas que domina:")
            desafio_superado = st.text_area("Um problema complexo que resolveu:")

        botao_pagar = st.form_submit_button(f"PAGAR {preco} E GERAR DOCUMENTOS")

        if botao_pagar:
            with st.spinner(f"Aplicando {metodo_nome} via Inteligência Artificial..."):
                # --- O PROMPT AGRESSIVO ---
                prompt_final = f"""
                ATUE COMO UM HEADHUNTER SÊNIOR. 
                Gere um Currículo e uma Carta de Apresentação Agressiva.
                MÉTODO: {framework} (Foco em resultados e palavras-chave ATS).
                VAGA: {vaga_link}
                SALÁRIO ALVO: R$ {salario}
                DADOS DO CANDIDATO: {cv_atual}
                RESULTADO CHAVE: {resultado_impacto} usando {ferramentas}.
                DESAFIO VENCIDO: {desafio_superado}
                
                RESPOSTA: Formate claramente com títulos 'CURRÍCULO' e 'CARTA DE APRESENTAÇÃO'.
                """
                
                try:
                    response = model.generate_content(prompt_final)
                    texto_gerado = response.text
                    
                    st.balloons()
                    st.success("✅ Documentos Gerados com Sucesso!")
                    
                    tab1, tab2 = st.tabs(["📄 Currículo Estruturado", "✉️ Carta de Ataque"])
                    
                    # Dividindo a resposta (ajuste conforme o retorno da IA)
                    with tab1:
                        st.markdown(texto_gerado.split('CARTA DE APRESENTAÇÃO')[0])
                    with tab2:
                        if 'CARTA DE APRESENTAÇÃO' in texto_gerado:
                            st.markdown(texto_gerado.split('CARTA DE APRESENTAÇÃO')[1])
                        else:
                            st.markdown(texto_gerado)
                            
                except Exception as e:
                    st.error(f"Erro na geração: {e}")
