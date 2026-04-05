import requests
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import time

def minerar_adzuna():
    # --- CONFIGURAÇÃO API ADZUNA (COLOQUE SEUS DADOS AQUI) ---
    APP_ID = "ab71900e"
    APP_KEY = "483cf9166adf512b1daf45d49875509b"
    
    # 1. Conexão Google Sheets
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    try:
        creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
        client = gspread.authorize(creds)
        spreadsheet_id = "1hmGLBrUJxO8mZkqcZ6KsF3IXjV3_H8TNCnRHnjuukuo"
        sheet = client.open_by_key(spreadsheet_id).sheet1
        print("✅ Planilha conectada!")

        # 2. Busca de Vagas (Focando em SESI, SENAI e Indústria em SP)
        url = f"https://api.adzuna.com/v1/api/jobs/br/search/1"
        params = {
            "app_id": APP_ID,
            "app_key": APP_KEY,
            "results_per_page": 10,
            "what": "SESI SENAI industria",
            "where": "São Paulo",
            "content-type": "application/json"
        }

        print("🛰️ Consultando API oficial da Adzuna...")
        response = requests.get(url, params=params)
        
        if response.status_code != 200:
            print(f"❌ Erro na API: {response.status_code}")
            return

        vagas = response.json().get('results', [])
        print(f"📦 {len(vagas)} vagas encontradas!")

        for vaga in vagas:
            linha = [
                vaga.get('id'),
                vaga.get('title'),
                vaga.get('company', {}).get('display_name', 'N/A'),
                vaga.get('location', {}).get('display_name', 'SP'),
                "SP",
                "Presencial",
                "A consultar",
                "Educação/Indústria",
                vaga.get('redirect_url'),
                "Ativa"
            ]
            sheet.append_row(linha)
            print(f"✔️ Salva: {vaga.get('title')}")

        print("🚀 SUCESSO TOTAL!")

    except Exception as e:
        print(f"❌ ERRO: {e}")

if __name__ == "__main__":
    minerar_adzuna()
