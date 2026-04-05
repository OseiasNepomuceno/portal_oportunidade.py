import requests
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import time

def minerar_adzuna():
    # --- CONFIGURAÇÃO API ADZUNA ---
    APP_ID = "ab71900e"
    APP_KEY = "483cf9166adf512b1daf45d49875509b"
    
    # 1. Conexão Google Sheets
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    try:
        print("🔐 Carregando credenciais...")
        creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
        client = gspread.authorize(creds)
        
        # Seu ID de planilha confirmado
        spreadsheet_id = "1hmGLBrUJxO8mZkqcZ6KsF3IXjV3_H8TNCnRHnjuukuo"
        sheet = client.open_by_key(spreadsheet_id).sheet1
        print("✅ Planilha conectada!")

        # 2. Busca de Vagas (Bloco Ajustado para maior alcance)
        url = f"https://api.adzuna.com/v1/api/jobs/br/search/1"
        params = {
            "app_id": APP_ID,
            "app_key": APP_KEY,
            "results_per_page": 15,          # Aumentado para trazer mais opções
            "what": "vagas industria ensino", # Termos amplos que englobam SESI/SENAI
            "where": "Estado de São Paulo",   # Busca em todo o estado para não vir zerado
            "content-type": "application/json",
            "max_days_old": 30                # Apenas vagas recentes (último mês)
        }

        print("🛰️ Consultando API oficial da Adzuna...")
        response = requests.get(url, params=params)
        
        if response.status_code != 200:
            print(f"❌ Erro na API: {response.status_code}")
            return

        vagas = response.json().get('results', [])
        print(f"📦 {len(vagas)} vagas encontradas!")

        # 3. Gravando na Planilha
        for vaga in vagas:
            # Limpeza básica do título (remove tags HTML se houver)
            titulo = vaga.get('title', 'N/A').replace('<strong>', '').replace('</strong>', '')
            
            linha = [
                vaga.get('id'),
                titulo,
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
            print(f"✔️ Salva: {titulo}")
            time.sleep(0.5) # Pequena pausa para estabilidade

        print("🚀 SUCESSO TOTAL! Dados enviados para a planilha.")

    except Exception as e:
        print(f"❌ ERRO GERAL: {e}")

if __name__ == "__main__":
    minerar_adzuna()
