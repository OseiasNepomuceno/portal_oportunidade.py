import streamlit as st
import google.generativeai as genai
from groq import Groq
from fpdf import FPDF
import requests
import io

# --- CONFIGURAÇÃO DAS APIs ---
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    client_groq = Groq(api_key=st.secrets["GROQ_API_KEY"])
    
    safety_settings = [
        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
    ]
except Exception as e:
    st.error(f"Erro nas Chaves de API: {e}")

# --- LÓGICA DE INTELIGÊNCIA HÍBRIDA ---
def gerar_conteudo_ia(prompt):
    try:
        model_gemini = genai.GenerativeModel(model_name='gemini-1.5-flash')
        response = model_gemini.generate_content(prompt, safety_settings=safety_settings)
        return response.text, "Motor Gemini"
    except Exception:
        try:
            chat_completion = client_groq.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama-3.3-70b-versatile",
            )
            return chat_completion.choices[0].message.content, "Motor Groq (Llama 3.3)"
        except Exception as e_groq:
            return f"ERRO_TOTAL: {e_groq}", "Falha"

# --- FUNÇÕES DE APOIO ---
def notificar_venda_planilha(dados):
    WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbwNf3VrNaXJ7Tn2sohVG0XxGk_Ia94UIKP7Aq1FeXRHIWF1oKa_FyJHRs5xeSavzT8QQA/exec" 
    try:
        requests.post(WEBHOOK_URL, json=dados, timeout=5)
    except:
        pass 

def gerar_pdf(texto, template_name, nome_cliente):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    if template_name == "Executive":
        pdf.set_font("Helvetica", 'B', 16)
        pdf.cell(200, 10, txt=f"CURRICULO: {nome_cliente.upper()}", ln=True, align='C')
        pdf.ln(5)
        pdf.set_font("Helvetica", size=11)
    elif template_name == "Tech/Modern":
        pdf.set_fill_color(30, 41, 59)
        pdf.rect(0, 0, 210, 40, 'F')
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Helvetica", 'B', 18)
        pdf.cell(200, 25, txt=nome_cliente.upper(), ln=True, align='C')
        pdf.ln(10)
        pdf.set_text_color(0, 0, 0)
        pdf.set_font("Helvetica", size=10)
    else: 
        pdf.set_font("Courier", size=10)
        pdf.cell(200, 10, txt=nome_cliente.upper(), ln=True, align='L')
        pdf.ln(2)

    texto_limpo = texto.encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 7, txt=texto_limpo)
    return pdf.output(dest='S').encode('latin-1')

# --- INTERFACE ---
# 1. Ajuste: Título da Aba (Navegador)
st.set_page_config(page_title="Currículo de Alta Performance", layout="wide")

# Inicialização de variáveis de estado
if "diagnostico" not in st.session_state: st.session_state.diagnostico = False
if "sucesso" not in st.session_state: st.session_state.sucesso = False
if "pdf_bytes" not in st.session_state: st.session_state.pdf_bytes = None
if "texto_gerado" not in st.session_state: st.session_state.texto_gerado = ""

# 2. Ajuste: Título Principal (Header)
st.title("🚀 Currículo de Alta Performance: Engenharia de Carreira")

col1, col2 = st.columns(2)
with col1:
    st.subheader("📋 Dados da Vaga")
    nome_user = st.text_input("Seu Nome Completo:")
    vaga_desc = st.text_area("Descrição da Vaga/Requisitos:", height=150)
    salario = st.number_input("Pretensão Salarial (R$):", min_value=1500, step=500, value=3500)
with col2:
    st.subheader("👤 Seu Histórico")
    graduacao = st.selectbox("Sua Graduação:", ["Ensino Médio", "Técnico", "Graduação", "Pós/MBA", "Mestrado/Doc"])
    cv_atual = st.text_area("Cole seu Currículo Atual:", height=150)

# Lógica de Preços
if salario >= 10000:
    plano, preco_str, framework = "EXECUTIVE", "197,00", "ELITE"
elif 5000 <= salario < 10000:
    plano, preco_str, framework = "PRO", "97,00", "WHO/CAR"
else:
    plano, preco_str, framework = "START", "47,00", "STAR"

if st.button("⚡ GERAR DIAGNÓSTICO DE IMPACTO"):
    st.session_state.diagnostico = True

if st.session_state.diagnostico:
    st.markdown("---")
    col_diag, col_parceiro = st.columns([2, 1])
    with col_diag:
        st.error(f"⚠️ **URGÊNCIA:** Vagas de R$ {salario} exigem Engenharia de Impacto.")
    with col_parceiro:
        st.subheader("👨‍💼 Validação Profissional")
        parceiros_rh = {"Indicação Direta": "ORG000", "Oseias Nepomuceno": "RH001", "Ricardo Souza": "RH002", "Camila Oliveira": "RH003"}
        consultor = st.selectbox("Quem recomendou?", list(parceiros_rh.keys()))

    with st.form("provas_competencia"):
        resultado = st.text_area("Seu maior resultado real:")
        ferramentas = st.text_input("Ferramentas que domina:")
        desafio = st.text_area("Um problema difícil resolvido:")
        template_choice = st.radio("Estilo do PDF:", ["Tech/Modern", "Executive", "Minimalist"])
        pagar = st.form_submit_button(f"LIBERAR CURRÍCULO {plano}")

        if pagar:
            valor_venda = float(preco_str.replace(',', '.'))
            valor_comissao = valor_venda * 0.30 if parceiros_rh[consultor] != "ORG000" else 0.0
            
            notificar_venda_planilha({
                "cliente": nome_user, 
                "plano": plano, 
                "valor": valor_venda,
                "comissao": valor_comissao, 
                "consultor": consultor, 
                "id_rh": parceiros_rh[consultor]
            })

            with st.spinner("Processando Inteligência Híbrida..."):
                prompt = f"Aja como Headhunter Sênior. Gere um CV e carta para a vaga: {vaga_desc}. Candidato: {nome_user}, {graduacao}. Experiência: {cv_atual}. Resultado: {resultado}. Framework: {framework}."
                texto_ia, motor = gerar_conteudo_ia(prompt)
                
                if "ERRO_TOTAL" not in texto_ia:
                    st.session_state.texto_gerado = texto_ia
                    st.session_state.pdf_bytes = gerar_pdf(texto_ia, template_choice, nome_user)
                    st.session_state.motor_usado = motor
                    st.session_state.sucesso = True

# --- ÁREA DE ENTREGA (FORA DO FORMULÁRIO) ---
if st.session_state.sucesso:
    st.markdown("---")
    st.info(f"✨ {st.session_state.motor_usado}")
    st.success("Documentos Estruturados com Sucesso!")
    
    c_pay, c_down = st.columns(2)
    with c_pay:
        st.markdown(f'''<a href="https://www.mercadopago.com.br" target="_blank"><button style="background-color: #009EE3; color: white; padding: 12px; border: none; border-radius: 5px; width: 100%; cursor: pointer; font-weight: bold; width: 100%;">1. FINALIZAR PAGAMENTO (R$ {preco_str})</button></a>''', unsafe_allow_html=True)
    with c_down:
        # 3. Ajuste: Nome do Arquivo de Download
        st.download_button(
            label="2. BAIXAR CURRÍCULO (PDF)",
            data=st.session_state.pdf_bytes,
            file_name=f"Curriculo_Alta_Performance_{nome_user.replace(' ', '_')}.pdf",
            mime="application/pdf",
            key="btn_download_v3"
        )
    
    st.subheader("📝 Prévia")
    st.text_area("Conteúdo IA:", value=st.session_state.texto_gerado, height=300)
    st.balloons()
