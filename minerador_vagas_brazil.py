import pandas as pd
import requests
import os
import json
import gspread
from datetime import datetime, timedelta
from oauth2client.service_account import ServiceAccountCredentials

def obter_chave(nome):
    """Busca as chaves nas variáveis de ambiente do GitHub Actions"""
    return os.environ.get(nome)

def conectar_google_direto():
    """Conecta na planilha usando a biblioteca oficial (gspread)"""
    scope = ['https://www.googleapis.com/auth/spreadsheets', "https://www.googleapis.com/auth/drive"]
    
    # Busca o JSON da Service Account guardado nos Secrets do GitHub
    js_creds = json.loads(obter_chave("GCP_SERVICE_ACCOUNT"))
    creds = ServiceAccountCredentials.from_json_keyfile_dict(js_creds, scope)
    client = gspread.authorize(creds)
    
    # Abre a planilha pela URL guardada nos Secrets
    return client.open_by_url(obter_chave("GSHEETS_URL")).get_worksheet(0)

def minerar_vagas():
    vagas = []
    hoje = datetime.now().strftime("%Y-%m-%d")
    aid, akey = obter_chave("APP_ID"), obter_chave("APP_KEY")
    serp_key = obter_chave("SERPAPI_KEY")

    # Função interna para garantir que cada coluna receba o dado correto
    def formatar_linha(titulo, empresa, cidade, fonte, link):
        return [
            "",               # [0] Coluna A: ID (preenchido no executar)
            titulo,           # [1] Coluna B: Título
            empresa,          # [2] Coluna C: Empresa
            cidade,           # [3] Coluna D: Cidade
            "BR",             # [4] Coluna E: UF
            "Ver na Fonte",   # [5] Coluna F: Tipo
            0,                # [6] Coluna G: Salário
            fonte,            # [7] Coluna H: Fonte
            "Geral",          # [8] Coluna I: Área
            link,             # [9] Coluna J: Link_Inscrição
            "Ativa",          # [10] Coluna K: Status (Essencial para o filtro do App)
            hoje              # [11] Coluna L: Data_Captura
        ]

    # --- CAPTURA 1: ADZUNA ---
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

    # --- CAPTURA 2: GOOGLE JOBS (SERPAPI) ---
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
            # Calcula o ID sequencial baseando-se nas linhas já existentes
            valores_atuais = sheet.get_all_values()
            proximo_id = len(valores_atuais) 
            
            for i, vaga in enumerate(novas_vagas):
                vaga[0] = proximo_id + i 
            
            # Insere as linhas no final da planilha com formatação de usuário (para links funcionarem)
            sheet.append_rows(novas_vagas, value_input_option='USER_ENTERED')
            print(f"✅ {len(novas_vagas)} vagas adicionadas com sucesso nas colunas corretas!")
        else:
            print("⚠️ Nenhuma vaga nova encontrada.")
    except Exception as e:
        print(f"❌ Erro ao executar minerador: {e}")

if __name__ == "__main__":
    executar()
