import streamlit as st

# Configuração da Página
st.set_page_config(page_title="Engenharia de Carreira IA", layout="wide", page_icon="🚀")

st.title("🚀 Inteligência de Aprovação: O Currículo Irrecusável")
st.markdown("---")

# --- LÓGICA DE ESTADO (SESSION STATE) ---
# Isso garante que o formulário apareça e permaneça na tela
if "mostrar_diagnostico" not in st.session_state:
    st.session_state.mostrar_diagnostico = False

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

# Definição automática de Plano e Framework
if salario >= 10000:
    plano, preco, metodo = "EXECUTIVE", "R$ 197,00", "ELITE"
elif 5000 <= salario < 10000:
    plano, preco, metodo = "PRO", "R$ 97,00", "WHO/CAR"
else:
    plano, preco, metodo = "START", "R$ 47,00", "STAR"

# Botão para disparar o diagnóstico
if st.button("⚡ GERAR DIAGNÓSTICO DE IMPACTO"):
    st.session_state.mostrar_diagnostico = True

# --- CAMADA 2: DIAGNÓSTICO E FORMULÁRIO DE COMPETÊNCIAS ---
if st.session_state.mostrar_diagnostico:
    st.markdown("---")
    st.markdown(f"### 🎯 Diagnóstico Estratégico: Plano **{plano}**")
    
    col_diag1, col_diag2 = st.columns([2, 1])
    
    with col_diag1:
        st.error(f"⚠️ **URGÊNCIA:** Vagas de R$ {salario} exigem o método **{metodo}**. Seu modelo atual corre risco de descarte.")
        st.info(f"✅ **Estratégia:** Reestruturaremos seu perfil focado em **{', '.join(exp_possuida)}** para vencer os filtros ATS.")
    
    with col_diag2:
        st.metric("Aderência Atual", "35%", "-65% de GAP")

    st.markdown("---")
    
    # --- FORMULÁRIO DE PROVAS DE COMPETÊNCIA ---
    st.subheader("🛠️ Provas de Competência (Ouro para a IA)")
    st.write("Insira informações reais para que a IA gere os argumentos que os recrutadores buscam.")
    
    # Usamos o formulário aqui
    with st.form("form_competencias"):
        c1, c2 = st.columns(2)
        with c1:
            tempo_exp = st.selectbox("Tempo de experiência na função:", 
                                    ["Iniciante", "1-3 anos", "3-5 anos", "5-10 anos", "10+ anos"])
            resultado_impacto = st.text_area("Seu maior resultado real (Números, metas, elogios):", placeholder="Ex: Aumentei a produção em 15%...")
        with c2:
            ferramentas = st.text_input("Ferramentas/Softwares usados:", placeholder="Ex: Excel, Python, SAP...")
            desafio_superado = st.text_area("Um problema difícil que você resolveu:", placeholder="Como você agiu sob pressão?")

        # Seção Executiva condicional
        if salario >= 8000:
            st.markdown("**🎖️ Detalhes de Liderança e ROI**")
            lideranca = st.text_input("Tamanho da equipe ou orçamento gerenciado:")

        st.markdown("### 🔓 Concluir Engenharia de Carreira")
        botao_pagar = st.form_submit_button(f"PAGAR {preco} E GERAR CURRÍCULO {plano}")

        if botao_pagar:
            st.success(f"💳 Pagamento Identificado! Aplicando método {metodo}... Seu currículo está sendo gerado.")
            # Aqui você conectaria o seu prompt final para a IA
