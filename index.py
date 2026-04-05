import streamlit as st
import pandas as pd
from datetime import datetime

# Configuração da Página
st.set_page_config(page_title="Portal de Oportunidades | CoreGov", page_icon="💼", layout="wide")

# --- ESTILIZAÇÃO CUSTOMIZADA (CSS) ---
st.markdown("""
    <style>
    .vaga-card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #007bff;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
        margin-bottom: 15px;
    }
    .titulo-vaga { color: #007bff; font-size: 20px; font-weight: bold; }
    .empresa-vaga { color: #555; font-size: 16px; }
    .info-vaga { font-size: 14px; color: #777; margin-top: 5px; }
    </style>
""", unsafe_allow_html=True)

# --- FUNÇÕES DE APOIO ---
def carregar_dados():
    # Aqui simulamos a leitura de um CSV ou Banco de Dados
    # Futuramente: df = pd.read_csv('vagas.csv')
    vagas = [
        {"id": 1, "titulo": "Analista Administrativo", "empresa": "CoreGov Consultoria", "cidade": "Rio de Janeiro", "uf": "RJ", "tipo": "Remoto", "salario": 3500.00, "area": "Administrativo"},
        {"id": 2, "titulo": "Consultor de Licitações", "empresa": "GovTech", "cidade": "São Paulo", "uf": "SP", "tipo": "Híbrido", "salario": 5000.00, "area": "Consultoria"},
        {"id": 3, "titulo": "Auxiliar de RH", "empresa": "Parceiro Local", "cidade": "Frutal", "uf": "MG", "tipo": "Presencial", "salario": 2200.00, "area": "Recursos Humanos"}
    ]
    return pd.DataFrame(vagas)

# --- INTERFACE PRINCIPAL ---
def main():
    st.title("💼 Portal de Oportunidades")
    st.subheader("Sua ponte para o mercado de trabalho especializado")

    df_vagas = carregar_dados()

    # --- FILTROS ---
    with st.sidebar:
        st.image("https://via.placeholder.com/150x50?text=CoreGov+Logo", use_column_width=True) # Coloque sua logo aqui
        st.header("Filtrar Oportunidades")
        
        busca = st.text_input("🔍 O que você busca?", placeholder="Cargo ou palavra-chave")
        
        uf_filtro = st.multiselect("Estado (UF):", options=sorted(df_vagas['uf'].unique()), default=sorted(df_vagas['uf'].unique()))
        
        tipo_filtro = st.multiselect("Modalidade:", options=df_vagas['tipo'].unique(), default=df_vagas['tipo'].unique())
        
        st.divider()
        st.caption("Desenvolvido por Oseias | CoreGov 2026")

    # --- LÓGICA DE FILTRAGEM ---
    df_filtrado = df_vagas[
        (df_vagas['uf'].isin(uf_filtro)) & 
        (df_vagas['tipo'].isin(tipo_filtro))
    ]
    
    if busca:
        df_filtrado = df_filtrado[df_filtrado['titulo'].str.contains(busca, case=False) | df_filtrado['empresa'].str.contains(busca, case=False)]

    # --- EXIBIÇÃO ---
    st.write(f"Exibindo **{len(df_filtrado)}** vaga(s) encontrada(s):")

    for _, vaga in df_filtrado.iterrows():
        st.markdown(f"""
            <div class="vaga-card">
                <div class="titulo-vaga">{vaga['titulo']}</div>
                <div class="empresa-vaga">🏢 {vaga['empresa']}</div>
                <div class="info-vaga">📍 {vaga['cidade']} - {vaga['uf']} | 💻 {vaga['tipo']}</div>
                <div class="info-vaga">💰 R$ {vaga['salario']:.2f}</div>
            </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button(f"Ver Detalhes", key=f"detalhe_{vaga['id']}"):
                st.toast(f"Abrindo detalhes para {vaga['titulo']}...")
        st.write("") # Espaçador entre cards

if __name__ == "__main__":
    main()
