import streamlit as st

# Configuração da Página
st.set_page_config(page_title="Engenharia de Carreira IA", layout="wide", page_icon="🚀")

st.title("🚀 Inteligência de Aprovação: O Currículo Irrecusável")
st.markdown("---")

# --- LÓGICA DE ESTADO (SESSION STATE) ---
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

# Definição Interna de Plano e Métodos (Back-end)
if salario >= 10000:
    plano, preco = "EXECUTIVE", "R$ 197,00"
    nomenclatura_metodo = "Protocolo de Liderança e ROI Executivo"
    framework_interno = "ELITE"
elif 5000 <= salario < 10000:
    plano, preco = "PRO", "R$ 97,00"
    nomenclatura_metodo = "Método de Alta Performance e Resultados Técnicos"
    framework_interno = "WHO/CAR"
else:
    plano, preco = "START", "R$ 47,00"
    nomenclatura_metodo = "Engenharia de Competências e Impacto Imediato"
    framework_interno = "STAR"

# Botão para disparar o diagnóstico
if st.button("⚡ GERAR DIAGNÓSTICO DE IMPACTO"):
    st.session_state.mostrar_diagnostico = True

# --- CAMADA 2: DIAGNÓSTICO E FORMULÁRIO DE COMPETÊNCIAS ---
if st.session_state.mostrar_diagnostico:
    st.markdown("---")
    st.markdown(f"### 🎯 Diagnóstico Estratégico: Nível **{plano}**")
    
    col_diag1, col_diag2 = st.columns([2, 1])
    
    with col_diag1:
        st.error(f"⚠️ **ALERTA DE URGÊNCIA:** Vagas de R$ {salario} exigem um **{nomenclatura_metodo}**. Seu modelo de currículo atual possui falhas estruturais que levam ao descarte automático pelos robôs de seleção (ATS).")
        st.info(f"✅ **Estratégia de Aprovação:** Nossa IA irá reconfigurar seu histórico profissional focando em **{', '.join(exp_possuida)}** para que você se destaque entre os 5% melhores candidatos.")
    
    with col_diag2:
        st.metric("Índice de Aderência", "28%", "-72% de GAP detectado")
        st.caption("Baseado nos requisitos da vaga informada.")

    st.markdown("---")
    
    # --- FORMULÁRIO DE PROVAS DE COMPETÊNCIA ---
    st.subheader("🛠️ Provas de Competência (Ouro para a IA)")
    st.write("Forneça os dados reais abaixo. Nossa tecnologia de IA converterá esses fatos em argumentos de venda imbatíveis.")
    
    with st.form("form_competencias"):
        c1, c2 = st.columns(2)
        with c1:
            tempo_exp = st.selectbox("Tempo de experiência na função:", 
                                    ["Iniciante/Transição", "1-3 anos", "3-5 anos", "5-10 anos", "10+ anos"])
            resultado_impacto = st.text_area("Cite um resultado ou meta batida (Use números, ex: 20%, R$ 10k, 50 atendimentos):", 
                                            placeholder="Ex: Reduzi o tempo de espera em 15%...")
        with c2:
            ferramentas = st.text_input("Ferramentas ou metodologias que domina:", placeholder="Ex: Excel, Python, SAP, Metodologia Ágil...")
            desafio_superado = st.text_area("Descreva um problema complexo que você resolveu com sucesso:", 
                                            placeholder="Como você agiu para evitar um prejuízo ou erro?")

        if salario >= 8000:
            st.markdown("**🎖️ Indicadores de Gestão e Impacto Financeiro**")
            lideranca = st.text_input("Qual o tamanho da equipe ou volume financeiro que você gerenciava?")

        st.markdown("### 🔓 Liberar Engenharia de Carreira")
        st.write(f"Ao confirmar, nossa IA aplicará o **{nomenclatura_metodo}** para gerar seu novo documento.")
        
        botao_pagar = st.form_submit_button(f"PAGAR {preco} E CONQUISTAR MINHA VAGA")

        if botao_pagar:
            # --- CAMADA 3: O GERADOR FINAL (IMPLEMENTAÇÃO) ---
            st.success(f"💳 Pagamento Identificado! Aplicando {nomenclatura_metodo}...")
            
            # Construção do Prompt Agressivo para a IA
            prompt_final = f"""
            ATUE COMO UM HEADHUNTER SÊNIOR E ESTRATEGISTA DE CARREIRA.
            OBJETIVO: Gerar Currículo e Carta de Apresentação Agressiva para vaga de R$ {salario}.
            MÉTODO INTERNO: {framework_interno}
            
            DADOS DA VAGA: {vaga_link}
            PERFIL ATUAL: {cv_atual}
            PROVAS DE IMPACTO: 
            - Resultado: {resultado_impacto}
            - Ferramentas: {ferramentas}
            - Desafio: {desafio_superado}
            
            ESTRUTURA DE SAÍDA:
            1. Headline Profissional de Alto Impacto.
            2. Experiências reescritas focando em ROI e RESULTADOS NUMÉRICOS.
            3. Carta de Apresentação 'Ataque': Identifique a dor da vaga e mostre que o candidato é a única solução.
            """
            
            st.markdown("---")
            st.subheader("📄 Seus Documentos de Alta Performance")
            
            # Tabs para organizar a entrega final
            tab_cv, tab_carta = st.tabs(["📄 Currículo Otimizado", "✉️ Carta de Apresentação"])
            
            with tab_cv:
                st.info(f"Este documento foi estruturado com o {nomenclatura_metodo}.")
                st.code(f"GERANDO CONTEÚDO PARA: {graduacao}...\n(Aqui a IA retornaria o texto formatado baseado no {framework_interno})", language="text")
                st.button("📥 Baixar Currículo em PDF (Simulação)")

            with tab_carta:
                st.warning("Esta carta foi desenhada para 'atacar' os requisitos da vaga.")
                st.code("GERANDO CARTA DE APRESENTAÇÃO ESTRATÉGICA...", language="text")
                st.button("📥 Baixar Carta em PDF (Simulação)")
            
            st.balloons()
