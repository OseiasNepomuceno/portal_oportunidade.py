import streamlit as st
import google.generativeai as genai
from groq import Groq # Importação da Groq
from fpdf import FPDF
import base64
import requests

# --- CONFIGURAÇÃO DAS APIs ---
try:
    # Google Gemini
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    
    # Groq (Acelerador de Emergência)
    client_groq = Groq(api_key=st.secrets["GROQ_API_KEY"])
    
    safety_settings = [
        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
    ]
except Exception as e:
    st.error(f"Erro nas Chaves de API: {e}")

# --- LÓGICA DE INTELIGÊNCIA HÍBRIDA (GEMINI + GROQ) ---
def gerar_conteudo_ia(prompt):
    """Tenta Gemini primeiro. Se falhar, usa Groq instantaneamente."""
    
    # Tentativa 1: Google Gemini (Flash)
    try:
        model_gemini = genai.GenerativeModel(model_name='gemini-1.5-flash')
        response = model_gemini.generate_content(prompt, safety_settings=safety_settings)
        return response.text, "Motor Gemini"
    except Exception as e:
        # Tentativa 2: Groq (Llama 3.3) - O "Tanque de Guerra"
        try:
            chat_completion = client_groq.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama-3.3-70b-versatile",
            )
            return chat_completion.choices[0].message.content, "Motor Groq (Alta Velocidade)"
        except Exception as e_groq:
            return f"ERRO_TOTAL: Ambos os motores falharam. {e_groq}", "Falha"

# --- FUNÇÕES DE APOIO ---
def notificar_venda_planilha(dados):
    WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbyHJggBgmsF8DI6F7SjV9gM0uQ6XZpq6JBAVkWqR_Lc-KmBVzXYZqk9rFxYAtP6Y6V0ow/exec" 
    try:
        requests.post(WEBHOOK_URL, json=dados, timeout=5)
    except:
        pass 

def gerar_pdf(texto, template_name, nome_cliente):
    pdf = FPDF()
    pdf.add_page()
    if template_name == "Executive":
        pdf.set_font("Times", 'B', 16)
        pdf.cell(200, 10, txt=f"CURRÍCULO: {nome_cliente.upper()}", ln=True, align='C')
        pdf.ln(5)
        pdf.set_font("Times", size=11)
    elif template_name == "Tech/Modern":
        pdf.set_fill_color(30, 41, 59)
        pdf.rect(0, 0, 210, 40, 'F')
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Arial", 'B', 18)
        pdf.cell(200, 25, txt=nome_cliente.upper(), ln=True, align='C')
        pdf.ln(10)
        pdf.set_text_color(0, 0, 0)
        pdf.set_font("Arial", size=10)
    else: 
        pdf.set_font("Courier", size=10)
        pdf.cell(200, 10, txt=nome_cliente.upper(), ln=True, align='L')
        pdf.ln(2)
    pdf.multi_cell(0, 7, txt=texto.encode('latin-1', 'replace').decode('latin-1'))
    return pdf.output(dest='S').encode('latin-1')

# --- INTERFACE ---
st.set_page_config(page_title="Engenharia de Carreira IA", layout="wide")
if "diagnostico" not in st.session_state:
    st.session_state.diagnostico = False

st.title("🚀 Inteligência de Aprovação: O Currículo Irrecusável")
st.caption("Sistema Híbrido Gemini + Groq Ativado.")

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
        parceiros_rh = {
            "Indicação Direta": "ORG000",
            "Oseias Nepomuceno": "RH001",
            "Ricardo Souza": "RH002",
            "Camila Oliveira": "RH003"
        }
        consultor = st.selectbox("Quem recomendou?", list(parceiros_rh.keys()))

    with st.form("provas_competencia"):
        resultado = st.text_area("Seu maior resultado real:")
        ferramentas = st.text_input("Ferramentas que domina:")
        desafio = st.text_area("Um problema difícil resolvido:")
        template_choice = st.radio("Estilo do PDF:", ["Tech/Modern", "Executive", "Minimalist"])
        pagar = st.form_submit_button(f"LIBERAR CURRÍCULO {plano}")

        if pagar:
            valor_venda = float(preco_str.replace(',', '.'))
            PERCENTUAL_COMISSAO = 0.30
            valor_comissao = valor_venda * PERCENTUAL_COMISSAO if parceiros_rh[consultor] != "ORG000" else 0.0
            
            notificar_venda_planilha({
                "cliente": nome_user, "plano": plano, "valor": valor_venda,
                "comissao": valor_comissao, "consultor": consultor, "id_rh": parceiros_rh[consultor]
            })

            with st.spinner("Processando com Inteligência Híbrida..."):
                prompt = f"Aja como Headhunter Sênior. Gere um currículo focado em resultados e uma carta de apresentação para a vaga: {vaga_desc}. Candidato: {nome_user}, {graduacao}. Experiência: {cv_atual}. Resultado Chave: {resultado}. Use o framework {framework}."
                
                texto_ia, motor_usado = gerar_conteudo_ia(prompt)
                
                if "ERRO_TOTAL" in texto_ia:
                    st.error("Desculpe, ambos os motores de IA estão instáveis. Tente em 5 minutos.")
                else:
                    st.info(f"Processado via: {motor_usado}")
                    st.success("Documentos Gerados com Sucesso!")
                    
                    link_mp = "https://www.mercadopago.com.br"
                    st.markdown(f'''<a href="{link_mp}" target="_blank"><button style="background-color: #009EE3; color: white; padding: 12px; border: none; border-radius: 5px; width: 100%; cursor: pointer; font-weight: bold;">PAGAR AGORA (R$ {preco_str})</button></a>''', unsafe_allow_html=True)
                    
                    pdf_bytes = gerar_pdf(texto_ia, template_choice, nome_user)
                    st.download_button(label="📥 Baixar Currículo (PDF)", data=pdf_bytes, file_name=f"Curriculo_{nome_user.replace(' ', '_')}.pdf", mime="application/pdf")
                    st.markdown("---")
                    st.text(texto_ia)
                    st.balloons()
