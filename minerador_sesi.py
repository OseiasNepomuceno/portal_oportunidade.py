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
        spreadsheet_id = "COLOQUE_AQUI_O_ID_DA_SUA_PLANILHA" 
        
        print(f"📂 Abrindo planilha ID: {spreadsheet_id}")
        sheet = client.open_by_key(spreadsheet_id).sheet1
        print("✅ Conexão com a planilha estabelecida!")

        # 2. Busca de Dados
        url = "https://sesisenaisp.empregare.com/api/v1/vacancies/search"
        print("🛰️ Acessando API do SESI/SENAI...")
        response = requests.get(url, params={"page": 1, "limit": 10})
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
