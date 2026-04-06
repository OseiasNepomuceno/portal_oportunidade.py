import streamlit as st

st.set_page_config(page_title="Engenharia de Carreira IA", layout="wide")

st.title("🚀 Inteligência de Aprovação: O Currículo Irrecusável")
st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    st.subheader("📋 Dados da Oportunidade")
    vaga_link = st.text_area("Cole a Descrição da Vaga:")
    salario = st.number_input("Pretensão Salarial (R$):", min_value=1500, step=500)
    graduacao = st.selectbox("Sua Graduação:", ["Ensino Médio", "Técnico", "Graduação", "Pós/MBA", "Mestrado/Doc"])

with col2:
    st.subheader("👤 Seu Perfil Atual")
    exp_possuida = st.multiselect("O que você já domina?", ["Liderança", "Ferramentas Técnicas", "Gestão de Projetos", "Atendimento", "Vendas"])
    cv_atual = st.text_area("Cole seu Currículo Atual:")

if st.button("⚡ GERAR DIAGNÓSTICO DE IMPACTO"):
    # Lógica de Definição de Preço e Framework
    if salario >= 10000:
        plano = "EXECUTIVE"
        preco = "R$ 197,00"
        metodo = "ELITE"
    elif 5000 <= salario < 10000:
        plano = "PRO"
        preco = "R$ 97,00"
        metodo = "WHO/CAR"
    else:
        plano = "START"
        preco = "R$ 47,00"
        metodo = "STAR"

    st.markdown(f"### 🎯 Diagnóstico: Plano {plano}")
    st.error(f"⚠️ **URGÊNCIA:** Esta vaga de R$ {salario} exige o método **{metodo}**. Seu currículo atual corre risco de descarte automático.")
    
    st.info(f"✅ **O que faremos:** Reestruturaremos sua carreira para o nível {graduacao} com foco em {', '.join(exp_possuida)}.")
    
    st.subheader(f"🔓 Valor do Investimento: {preco}")
    if st.button(f"GERAR MEU CURRÍCULO {plano} AGORA"):
        st.success("Redirecionando para o Checkout seguro...")
