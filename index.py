import streamlit as st

# Configuração da Página
st.set_page_config(page_title="Engenharia de Carreira IA", layout="wide", page_icon="🚀")

st.title("🚀 Inteligência de Aprovação: O Currículo Irrecusável")
st.markdown("---")

# Inicialização de estados do sistema
if "diagnostico_gerado" not in st.session_state:
    st.session_state.diagnostico_gerado = False

# --- CAMADA 1: CAPTAÇÃO DE DADOS INICIAIS ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("📋 Dados da Oportunidade")
    vaga_link = st.text_area("Cole a Descrição da Vaga ou os Requisitos principais:", height=150)
    salario = st.number_input("Pretensão Salarial Aproximada (R$):", min_value=1500, step=500, value=3000)
    graduacao = st.selectbox("Sua Graduação Atual:", ["Ensino Médio", "Técnico", "Graduação", "Pós/MBA", "Mestrado/Doc"])

with col2:
    st.subheader("👤 Seu Perfil Atual")
    exp_possuida = st.multiselect("Selecione o que você já domina ou a vaga exige:", 
                                   ["Liderança", "Ferramentas Técnicas", "Gestão de Projetos", "Atendimento", "Vendas", "Operação Logística", "Análise de Dados"])
    cv_atual = st.text_area("Cole seu Currículo Atual ou resumo de experiências:", height=150)

# --- LÓGICA DE DEFINIÇÃO DE PLANO E FRAMEWORK ---
if salario >= 10000:
    plano, preco, metodo = "EXECUTIVE", "R$ 197,00", "ELITE"
elif 5000 <= salario < 10000:
    plano, preco, metodo = "PRO", "R$ 97,00", "WHO/CAR"
else:
    plano, preco, metodo = "START", "R$ 47,00", "STAR"

# Botão Principal de Diagnóstico
if st.button("⚡ GERAR DIAGNÓSTICO DE IMPACTO"):
    st.session_state.diagnostico_gerado = True

# --- CAMADA 2: DIAGNÓSTICO E PROVAS DE COMPETÊNCIA ---
if st.session_state.diagnostico_gerado:
    st.markdown("---")
    st.markdown(f"### 🎯 Diagnóstico Estratégico: Plano **{plano}**")
    
    col_diag1, col_diag2 = st.columns([2, 1])
    
    with col_diag1:
        st.error(f"⚠️ **URGÊNCIA:** O mercado para salários de R$ {salario} não aceita currículos genéricos. "
                 f"Para ser aprovado, você precisa do método **{metodo}**.")
        st.info(f"✅ **Estratégia:** Reestruturaremos seu perfil de {graduacao} focando em **{', '.join(exp_possuida)}** "
                f"para passar nos filtros de IA (ATS) dos recrutadores.")
    
    with col_diag2:
        st.metric("Aderência Atual", "35%", "-65% de GAP")
        st.write("Seu currículo atual está focado em 'tarefas'. Vamos transformá-lo em 'resultados'.")

    st.markdown("---")
    
    # --- FORMULÁRIO DE PROVAS DE COMPETÊNCIA (O CORAÇÃO DO MIX) ---
    st.subheader("🛠️ Provas de Competência (Ouro para a IA)")
    st.write("Responda abaixo para que nossa IA insira as informações que os recrutadores *realmente* querem encontrar.")
    
    with st.form("form_competencias"):
        c1, c2 = st.columns(2)
        with c1:
            tempo_exp = st.selectbox("Quanto tempo de experiência possui nessa área específica?", 
                                    ["Nenhuma / Transição", "Menos de 1 ano", "1 a 3 anos", "3 a 5 anos", "Mais de 5 anos"])
            resultado_impacto = st.text_area("Qual foi seu maior resultado real? (Ex: Atendi 50 clientes/dia, economizei 10% de material, bati meta X)",
                                            placeholder="Use números e fatos!")
        with c2:
            ferramentas = st.text_input("Quais ferramentas/softwares você usou para gerar esse resultado?",
                                        placeholder="Ex: Excel, Python, SAP, CRM, Máquinas Industriais...")
            desafio_superado = st.text_area("Descreva um problema difícil que você resolveu:",
                                            placeholder="Ex: O sistema caiu e eu recuperei manualmente...")

        # Seção Bônus para Salários Altos
        if salario >= 8000:
            st.markdown("**🎖️ Detalhes de Liderança e ROI**")
            lideranca = st.text_input("Tamanho da equipe liderada ou orçamento gerenciado (se houver):")

        # --- CAMADA 3: FECHAMENTO E PAGAMENTO ---
        st.markdown("### 🔓 Concluir Engenharia de Carreira")
        st.write(f"Ao clicar abaixo, nossa IA processará o método **{metodo}** para gerar seu novo Currículo e Carta de Apresentação.")
        
        botao_pagar = st.form_submit_button(f"PAGAR {preco} E GERAR CURRÍCULO {plano}")

        if botao_pagar:
            st.toast("Processando Pagamento...", icon="💰")
            st.success(f"Pagamento Identificado! Gerando currículo {plano} com método {metodo}... Aguarde.")
            # Aqui entraria a chamada da API do Gemini enviando todas as variáveis coletadas
