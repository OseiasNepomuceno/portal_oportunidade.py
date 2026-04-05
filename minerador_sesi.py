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
        # Esta é a URL exata que o sistema Empregare usa para o SESI SP
        url = "https://sesisenaisp.empregare.com/api/v1/vacancies/search"
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "pt-BR,pt;q=0.9",
            "Origin": "https://sesisenaisp.empregare.com",
            "Referer": "https://sesisenaisp.empregare.com/pt-br/vagas"
        }
        
        # Parâmetros que o site envia para trazer as vagas recentes
        params = {
            "page": 1,
            "limit": 20,
            "sorting": "newest",
            "is_active": "true"
        }
        
        print("🛰️ Acessando portal de vagas SESI/SENAI...")
        response = requests.get(url, params=params, headers=headers)
        
        if response.status_code != 200:
            print(f"❌ Erro de acesso: {response.status_code}. O site pode estar em manutenção.")
            return

        # Tentando ler os dados com segurança
        dados_json = response.json()
        vagas = dados_json.get('data', [])
        
        if not vagas:
            print("⚠️ Nenhuma vaga encontrada no momento.")
            return

        print(f"📦 {len(vagas)} vagas encontradas! Enviando para a planilha...")
        
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
