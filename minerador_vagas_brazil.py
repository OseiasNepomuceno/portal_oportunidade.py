import pandas as pd
import requests
import os
import json  # Essencial para processar a chave do Google
from datetime import datetime, timedelta
from streamlit_gsheets import GSheetsConnection
import streamlit as st

# --- FUNÇÃO HÍBRIDA PARA PEGAR AS CHAVES ---
def obter_chave(nome_da_chave):
    # 1. Tenta pegar do GitHub Actions (Environment)
    valor = os.environ.get(nome_da_chave)
    if valor:
        return valor
    # 2. Se não achar, tenta do Streamlit Secrets
    try:
        return st.secrets[nome_da_chave]
    except:
        return None

# --- CONFIGURAÇÕES ---
DIAS_LIMITE = 30

def carregar_dados_existentes():
    try:
        # Tenta usar a conta de serviço se estiver no GitHub
        service_account_info = os.environ.get("GCP_SERVICE_ACCOUNT")
        if service_account_info:
            credentials_dict = json.loads(service_account_info)
            conn = st.connection("gsheets", type=GSheetsConnection, service_account=credentials_dict)
        else:
            conn = st.connection("gsheets", type=GSheetsConnection)
            
        return conn.read(ttl=0).dropna(how="all")
    except Exception as e:
        print(f"Erro ao carregar dados: {e}")
        return pd.DataFrame()

def minerar_vagas_novas():
    vagas_novas = []
    hoje = datetime.now().strftime("%Y-%m-%d")

    # PEGANDO AS CHAVES DE FORMA SEGURA
    aid = obter_chave("APP_ID")
    akey = obter_chave("APP_KEY")
    serp_key = obter_chave("SERPAPI_KEY")

    # 1. CAPTURA ADZUNA
    if aid and akey:
        try:
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
                    "Fonte": "Adzuna",
                    "Área": "Geral",
                    "Link_Inscrição": item.get('redirect_url'),
                    "Status": "Ativa",
                    "Data_Captura": hoje
                })
        except Exception as e: print(f"Erro Adzuna: {e}")

    # 2. CAPTURA GOOGLE JOBS
    if serp_key:
        try:
            url_serp = f"https://serpapi.com/search.json?engine=google_jobs&q=vagas+industria+brasil&hl=pt&gl=br&api_key={serp_key}"
            res_serp = requests.get(url_serp).json()
            for item in res_serp.get('jobs_results', []):
                vagas_novas.append({
                    "Título": item.get('title'),
                    "Empresa": item.get('company_name'),
                    "Cidade": item.get('location', 'Brasil'),
                    "UF": "BR",
                    "Tipo": "Ver na Fonte",
                    "Salário": 0,
                    "Fonte": "Google",
                    "Área": "Geral",
                    "Link_Inscrição": item.get('share_link'),
                    "Status": "Ativa",
                    "Data_Captura": hoje
                })
        except Exception as e: print(f"Erro Google Jobs: {e}")

    return pd.DataFrame(vagas_novas)

def atualizar_planilha():
    df_antigo = carregar_dados_existentes()
    df_novas = minerar_vagas_novas()
    
    if df_novas.empty and df_antigo.empty:
        print("⚠️ Nenhuma vaga encontrada.")
        return

    # Unir e remover duplicatas
    if not df_antigo.empty:
        df_total = pd.concat([df_antigo, df_novas]).drop_duplicates(subset=['Link_Inscrição'], keep='first')
    else:
        df_total = df_novas

    # Ordenar por data e gerar IDs
    df_total['Data_Captura'] = pd.to_datetime(df_total['Data_Captura'])
    df_total = df_total.sort_values(by='Data_Captura', ascending=False)
    
    # Limpeza por data limite
    data_corte = datetime.now() - timedelta(days=DIAS_LIMITE)
    df_total = df_total[df_total['Data_Captura'] >= data_corte]
    
    df_total['Data_Captura'] = df_total['Data_Captura'].dt.strftime("%Y-%m-%d")
    df_total['ID'] = range(1, len(df_total) + 1)

    # Organizar as 12 colunas exatas
    colunas = ["ID", "Título", "Empresa", "Cidade", "UF", "Tipo", "Salário", "Fonte", "Área", "Link_Inscrição", "Status", "Data_Captura"]
    df_total = df_total[colunas]

    try:
        # Autenticação para Escrita
        service_account_info = os.environ.get("GCP_SERVICE_ACCOUNT")
        if service_account_info:
            credentials_dict = json.loads(service_account_info)
            conn = st.connection("gsheets", type=GSheetsConnection, service_account=credentials_dict)
        else:
            conn = st.connection("gsheets", type=GSheetsConnection)
            
        conn.update(data=df_total)
        print(f"✅ Sucesso! Planilha atualizada com {len(df_total)} vagas.")
    except Exception as e:
        print(f"❌ Erro ao salvar no Google Sheets: {e}")

if __name__ == "__main__":
    atualizar_planilha()
