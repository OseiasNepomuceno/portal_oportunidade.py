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
    """Conecta na planilha usando a biblioteca oficial"""
    scope = ['https://www.googleapis.com/auth/spreadsheets', "https://www.googleapis.com/auth/drive"]
    js_creds = json.loads(obter_chave("GCP_SERVICE_ACCOUNT"))
    creds = ServiceAccountCredentials.from_json_keyfile_dict(js_creds, scope)
    client = gspread.authorize(creds)
    return client.open_by_url(obter_chave("GSHEETS_URL")).get_worksheet(0)

def minerar_vagas():
    vagas = []
    hoje = datetime.now().strftime("%Y-%m-%d")
    aid, akey = obter_chave("APP_ID"), obter_chave("APP_KEY")
    serp_key = obter_chave("SERPAPI_KEY")

    # Função para montar a linha EXATAMENTE na ordem das colunas da planilha
    def formatar_linha(titulo, empresa, cidade, fonte, link):
        return [
            "",               # [0] ID (Deixamos vazio para a planilha ou lógica posterior)
            titulo,           # [1] Título
            empresa,          # [2] Empresa
            cidade,           # [3] Cidade
            "BR",             # [4] UF
            "Ver na Fonte",   # [5] Tipo
            0,                # [6] Salário
            fonte,            # [7] Fonte
            "Geral",          # [8] Área
            link,             # [9] Link_Inscrição
            "Ativa",          # [10] Status
            hoje              # [11] Data_Captura
        ]

    # 1. Adzuna
    if aid and akey:
        try:
            url = f"https://api.adzuna.com/v1/api/jobs/br/search/1?app_id={aid}&app_key={akey}&results_per_page=50&what=industria%20tecnologia"
            res = requests.get(url).json()
            for item in res.get('results', []):
                vagas.append(formatar_linha(
                    item.get('title'), 
                    item.get('company', {}).get('display_name', 'Confidencial'),
                    item.get('location', {}).get('display_name', 'Brasil'),
                    "Adzuna",
                    item.get('redirect_url')
                ))
        except Exception as e: print(f"Erro Adzuna: {e}")

    # 2. Google Jobs (SerpApi)
    if serp_key:
        try:
            url = f"https://serpapi.com/search.json?engine=google_jobs&q=vagas+industria+brasil&hl=pt&gl=br&api_key={serp_key}"
            res = requests.get(url).json()
            for item in res.get('jobs_results', []):
                vagas.append(formatar_linha(
                    item.get('title'),
                    item.get('company_name'),
                    item.get('location', 'Brasil'),
                    "Google",
                    item.get('share_link')
                ))
        except Exception as e: print(f"Erro Google: {e}")
    
    return vagas

def executar():
    try:
        sheet = conectar_google_direto()
        novas_vagas = minerar_vagas()
        
        if novas_vagas:
            # Pegar o número da última linha para continuar o ID (opcional)
            ultima_linha = len(sheet.get_all_values())
            for i, vaga in enumerate(novas_vagas):
                vaga[0] = ultima_linha + i # Preenche o ID automaticamente
            
            # Adiciona as novas vagas nas colunas corretas
            sheet.append_rows(novas_vagas, value_input_option='USER_ENTERED')
            print(f"✅ {len(novas_vagas)} vagas adicionadas com sucesso nas colunas corretas!")
        else:
            print("⚠️ Nenhuma vaga nova encontrada.")
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    executar()
