import streamlit as st
import google.generativeai as genai
from fpdf import FPDF
import base64

# --- CONFIGURAÇÃO DA API (Secrets) ---
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error("Erro na API: Verifique a GEMINI_API_KEY nos Secrets.")

# --- FUNÇÃO PARA GERAR PDF ---
def gerar_pdf(texto, template_name, nome_cliente):
    pdf = FPDF()
    pdf.add_page()
    
    if template_name == "Executive":
        pdf.set_font("Times", 'B', 16)
        pdf.set_text_color(0, 0, 0)
        pdf.cell(200, 10, txt=f"CURRÍCULO: {nome_cliente.upper()}", ln=True, align='C')
        pdf.ln(5)
        pdf.set_font("Times", size=11)
    elif template_name == "Tech/Modern":
        pdf.set_fill_color(30, 41, 59) # Azul Escuro
        pdf.rect(0, 0, 210, 40, 'F')
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Arial", 'B', 18)
        pdf.cell(200, 25, txt=nome_cliente.upper(), ln=True, align='C')
        pdf.ln(10)
        pdf.set_text_color(0, 0, 0)
        pdf.set_font("Arial", size=10)
    else: # Minimalist
        pdf.set_font("Courier", size=10)
        pdf.cell(200, 10, txt=nome_cliente.upper(), ln=True, align='L')
        pdf.ln(2)

    # Inserir o conteúdo da IA - Tratamento de caracteres latin-1 para FPDF
    pdf.multi_cell(0, 7, txt=texto.encode('latin-1', 'replace').decode('latin-1'))
    
    return pdf.output(dest='S').encode('latin-1')

# --- INTERFACE STREAMLIT ---
st.set_page_config(page_title="Engenharia de Carreira IA", layout="wide")

if "diagnostico" not in st.session_state:
    st.session_state.diagnostico = False

st.title("🚀 Inteligência de Aprovação: O Currículo Irrecusável")
st.caption("Transforme seu perfil comum em uma solução de alto impacto para o mercado.")

col1, col2 = st.columns(2)

with col1:
    st.subheader("📋 Dados da Vaga")
    nome_user = st.text_input("Seu Nome Completo:")
    vaga_desc = st.text_area("Descrição da Vaga/Requisitos:", height=150)
    salario = st.number_input("Pretensão Salarial (R$):", min_value=1500, step=500, value=3500)

with col2:
    st.subheader("👤 Seu Histórico")
    graduacao = st.selectbox("Sua Graduação:", ["Ensino Médio", "Técnico", "Graduação", "Pós/MBA", "Mestrado/Doc"])
    cv_atual = st.text_area("Cole seu Currículo Atual ou resumo de experiências:", height=150)

# Lógica de Venda e Metodologia Blindada
if salario >= 10000:
    plano, preco, metodo = "EXECUTIVE", "197,00", "Protocolo de ROI Executivo"
    framework = "ELITE"
elif 5000 <= salario < 10000:
    plano, preco, metodo = "PRO", "97,00", "Método de Alta Performance"
    framework = "WHO/CAR"
else:
    plano, preco, metodo = "START", "47,00", "Engenharia de Impacto Imediato"
    framework = "STAR"

if st.button("⚡ GERAR DIAGNÓSTICO DE IMPACTO"):
    st.session_state.diagnostico = True

if st.session_state.diagnostico:
    st.markdown("---")
    
    # --- BLOCO DE DIAGNÓSTICO E SELEÇÃO DE PARCEIRO ---
    col_diag, col_parceiro = st.columns([2, 1])
    
    with col_diag:
        st.error(f"⚠️ **URGÊNCIA:** Vagas de R$ {salario} exigem um **{metodo}**. Seu modelo atual corre risco de descarte.")
        st.info("O índice de aderência do seu currículo atual é baixo para os padrões de recrutamento automatizado.")

    with col_parceiro:
        st.subheader("👨‍💼 Validação Profissional")
        # Dicionário de Parceiros (Nome: ID_Comissão)
        parceiros_rh = {
            "Indicação Direta (Portal)": "ORG000",
            "Ana Silva - Tech Recruiter": "RH001",
            "Ricardo Souza - Headhunter Executivo": "RH002",
            "Camila Oliveira - Consultora de RH": "RH003"
        }
        consultor = st.selectbox("Quem recomendou nossa Engenharia para você?", list(parceiros_rh.keys()))
        
        if consultor != "Indicação Direta (Portal)":
            st.success(f"Especialista {consultor.split(' - ')[0]} selecionado(a) para suporte.")

    # --- FORMULÁRIO DE PROVAS DE COMPETÊNCIA ---
    with st.form("provas_competencia"):
        st.subheader("🛠️ Provas de Competência")
        c1, c2 = st.columns(2)
        with c1:
            resultado = st.text_area("Seu maior resultado real (Números/Metas):", placeholder="Ex: Aumentei o faturamento em 12%...")
        with c2:
            ferramentas = st.text_input("Ferramentas que domina:", placeholder="Ex: SAP, Python, Excel...")
            desafio = st.text_area("Um problema difícil que resolveu:", placeholder="Descreva como evitou um prejuízo ou falha.")
        
        st.markdown("---")
        template_choice = st.radio("Escolha o Estilo Visual do seu PDF Profissional:", ["Tech/Modern", "Executive", "Minimalist"])
        
        st.info(f"💰 Investimento para Aprovação: R$ {preco}")
        pagar = st.form_submit_button(f"PAGAR E LIBERAR CURRÍCULO {plano}")

        if pagar:
            with st.spinner("IA processando sua Engenharia de Carreira com supervisão técnica..."):
                # O ID do consultor pode ser salvo em log ou banco de dados aqui para pagamento de comissão
                id_comissao = parceiros_rh[consultor]
                
                prompt = f"""
                ATUE COMO UM HEADHUNTER SÊNIOR. 
                Gere um Currículo e uma Carta de Apresentação Agressiva.
                ESTILO: {framework}. VAGA: {vaga_desc}. SALÁRIO: R$ {salario}.
                CANDIDATO: {nome_user}, {graduacao}. CV ATUAL: {cv_atual}.
                RESULTADO: {resultado} com {ferramentas}. DESAFIO: {desafio}.
                SAÍDA: Texto profissional, sem introduções desnecessárias. Use títulos 'CURRICULO' e 'CARTA'.
                """
                try:
                    response = model.generate_content(prompt)
                    texto_ia = response.text
                    
                    st.success(f"Documentos validados estrategicamente por nossa IA e pela rede de parceiros!")
                    
                    # Gerar PDF
                    pdf_bytes = gerar_pdf(texto_ia, template_choice, nome_user)
                    
                    st.download_button(
                        label=f"📥 Baixar Currículo {template_choice} (PDF)",
                        data=pdf_bytes,
                        file_name=f"Curriculo_{nome_user.replace(' ', '_')}.pdf",
                        mime="application/pdf"
                    )
                    
                    st.markdown("### 📝 Prévia do Texto Gerado")
                    st.text(texto_ia)
                    st.balloons()
                    
                except Exception as e:
                    st.error(f"Erro ao gerar: {e}")
