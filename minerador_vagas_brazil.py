import pandas as pd
import requests
import os
import json
import gspread
from datetime import datetime, timedelta
from oauth2client.service_account import ServiceAccountCredentials

def obter_chave(nome):
    return os.environ.get(nome)

def conectar_google_direto():
    """Conecta na planilha usando a biblioteca oficial, sem passar pelo Streamlit"""
    scope = ['https://www.googleapis.com/auth/spreadsheets', "https://www.googleapis.com/auth/drive"]
    js_creds = json.loads(obter_chave("GCP_SERVICE_ACCOUNT"))
    creds = ServiceAccountCredentials.from_json_keyfile_dict(js_creds, scope)
    client = gspread.authorize(creds)
    
    # Abre a planilha pela URL
    return client.open_by_url(obter_chave("GSHEETS_URL")).get_worksheet(0)

def minerar_vagas():
    vagas = []
    hoje = datetime.now().strftime("%Y-%m-%d")
    aid, akey = obter_chave("APP_ID"), obter_chave("APP_KEY")
    serp_key = obter_chave("SERPAPI_KEY")

    # Adzuna
    if aid and akey:
        try:
            url = f"https://api.adzuna.com/v1/api/jobs/br/search/1?app_id={aid}&app_key={akey}&results_per_page=50&what=industria%20tecnologia"
            res = requests.get(url).json()
            for item in res.get('results', []):
                vagas.append([
                    item.get('title'), item.get('company', {}).get('display_name'),
                    item.get('location', {}).get('display_name'), "BR",
                    "Remoto" if "remoto" in item.get('description', '').lower() else "Presencial",
                    item.get('salary_min', 0), "Adzuna", item.get('redirect_url'), hoje
                ])
        except: pass

    # Google Jobs (SerpApi)
    if serp_key:
        try:
            url = f"https://serpapi.com/search.json?engine=google_jobs&q=vagas+industria+brasil&hl=pt&gl=br&api_key={serp_key}"
            res = requests.get(url).json()
            for item in res.get('jobs_results', []):
                vagas.append([
                    item.get('title'), item.get('company_name'), item.get('location'), "BR",
                    "Ver na Fonte", 0, "Google", item.get('share_link'), hoje
                ])
        except: pass
    return vagas

def executar():
    try:
        sheet = conectar_google_direto()
        novas_vagas = minerar_vagas()
        
        if novas_vagas:
            # Adiciona as novas vagas no final da planilha
            sheet.append_rows(novas_vagas)
            print(f"✅ {len(novas_vagas)} vagas adicionadas com sucesso!")
        else:
            print("⚠️ Nenhuma vaga nova encontrada.")
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    executar()
