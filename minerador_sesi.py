import requests
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os

def minerar_e_salvar():
    # 1. Configuração de Acesso
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    
    try:
        print("🔐 Tentando carregar credenciais...")
        creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
        client = gspread.authorize(creds)
        
        # --- ATENÇÃO: SUBSTITUA PELO SEU ID REAL ABAIXO ---
        spreadsheet_id = "1hmGLBrUJxO8mZkqcZ6KsF3IXjV3_H8TNCnRHnjuukuo" 
        
        print(f"📂 Abrindo planilha ID: {spreadsheet_id}")
        sheet = client.open_by_key(spreadsheet_id).sheet1
        print("✅ Conexão com a planilha estabelecida!")

        # 2. Busca de Dados
        url = "https://sesisenaisp.empregare.com/api/v1/vacancies/search"
        
        # O "disfarce" para o site não bloquear o robô
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        
        print("🛰️ Acessando API do SESI/SENAI...")
        
        response = requests.get(url, params={"page": 1, "limit": 10}, headers=headers)
        
        # Verifica se o site respondeu com sucesso antes de tentar ler
        if response.status_code != 200:
            print(f"⚠️ O site do SESI retornou erro {response.status_code}")
            return

        vagas = response.json().get('data', [])
        print(f"📦 {len(vagas)} vagas encontradas no site.")

        
        # 3. Envio para Planilha
        for vaga in vagas:
            linha = [
                vaga.get('id'), 
                vaga.get('title'), 
                "SESI/SENAI SP", 
                vaga.get('city', {}).get('name'), 
                "SP", "Presencial", "A combinar", 
                vaga.get('area', {}).get('name'), 
                f"https://sesisenaisp.empregare.com/pt-br/vaga/{vaga.get('id')}", 
                "Ativa"
            ]
            sheet.append_row(linha)
            print(f"✔️ Vaga '{vaga.get('title')}' adicionada.")

        print("🚀 TUDO PRONTO! Verifique sua planilha agora.")

    except Exception as e:
        print(f"❌ ERRO DETALHADO: {e}")

if __name__ == "__main__":
    minerar_e_salvar()
