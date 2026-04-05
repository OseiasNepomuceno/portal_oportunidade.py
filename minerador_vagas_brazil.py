import pandas as pd
import requests
from datetime import datetime, timedelta
from streamlit_gsheets import GSheetsConnection
import streamlit as st

# --- CONFIGURAÇÕES ---
DIAS_LIMITE = 30
PLANILHA_URL = st.secrets["connections"]["gsheets"]["spreadsheet"]

def carregar_dados_existentes():
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        df = conn.read()
        return df.dropna(how="all")
    except:
        return pd.DataFrame()

def minerar_vagas_novas():
    vagas_novas = []
    hoje = datetime.now().strftime("%Y-%m-%d")

    # 1. CAPTURA ADZUNA
    try:
        aid, akey = st.secrets["APP_ID"], st.secrets["APP_KEY"]
        url = f"https://api.adzuna.com/v1/api/jobs/br/search/1?app_id={aid}&app_key={akey}&results_per_page=50&what=industria%20tecnologia"
        res = requests.get(url).json()
        for item in res.get('results', []):
            vagas_novas.append({
                "Título": item.get('title'),
                "Empresa": item.get('company', {}).get('display_name', 'Confidencial'),
                "Cidade": item.get('location', {}).get('display_name', 'Brasil'),
                "UF": "BR",
                "Tipo": "Remoto" if "remoto" in item.get('description', '').lower() else "Presencial",
                "Salário": item.get('salary_min', 0),
                "Área": "Geral",
                "Fonte": "Adzuna",
                "Link_Inscrição": item.get('redirect_url'),
                "Data_Captura": hoje,
                "Status": "Ativa"
            })
    except: pass

    # 2. CAPTURA GOOGLE JOBS (SerpApi)
    try:
        serp_key = st.secrets["SERPAPI_KEY"]
        url_serp = f"https://serpapi.com/search.json?engine=google_jobs&q=vagas+industria+brasil&hl=pt&gl=br&api_key={serp_key}"
        res_serp = requests.get(url_serp).json()
        for item in res_serp.get('jobs_results', []):
            vagas_novas.append({
                "Título": item.get('title'),
                "Empresa": item.get('company_name'),
                "Cidade": item.get('location', 'Brasil'),
                "UF": "BR", # Pode usar a lógica de split que fizemos antes
                "Tipo": "Ver na Fonte",
                "Salário": 0,
                "Área": "Geral",
                "Fonte": "Google",
                "Link_Inscrição": item.get('share_link'),
                "Data_Captura": hoje,
                "Status": "Ativa"
            })
    except: pass

    return pd.DataFrame(vagas_novas)

def atualizar_planilha():
    df_antigo = carregar_dados_existentes()
    df_novas = minerar_vagas_novas()
    
    # 1. Unir e remover duplicatas baseadas no LINK
    if not df_antigo.empty:
        df_total = pd.concat([df_antigo, df_novas]).drop_duplicates(subset=['Link_Inscrição'], keep='first')
    else:
        df_total = df_novas

    # 2. LIMPEZA: Manter apenas os últimos 30 dias
    df_total['Data_Captura'] = pd.to_datetime(df_total['Data_Captura'])
    data_corte = datetime.now() - timedelta(days=DIAS_LIMITE)
    df_total = df_total[df_total['Data_Captura'] >= data_corte]
    
    # 3. Formatar data de volta para string para o Sheets
    df_total['Data_Captura'] = df_total['Data_Captura'].dt.strftime("%Y-%m-%d")

    # SALVAR (Aqui você usaria a função de escrita da biblioteca gsheets)
    # st.connection("gsheets", type=GSheetsConnection).update(data=df_total)
    
    print(f"Planilha atualizada! Total de vagas: {len(df_total)}")
    return df_total

if __name__ == "__main__":
    atualizar_planilha()
