import requests
from bs4 import BeautifulSoup
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import time

def minerar_indeed():
    # 1. Configuração Google Sheets
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    try:
        print("🔐 Carregando credenciais...")
        creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
        client = gspread.authorize(creds)
        
        # ID da sua planilha (Já atualizado com o seu!)
        spreadsheet_id = "1hmGLBrUJxO8mZkqcZ6KsF3IXjV3_H8TNCnRHnjuukuo"
        sheet = client.open_by_key(spreadsheet_id).sheet1
        print("✅ Conectado à planilha!")

        # 2. Busca no Indeed (Disfarçado de Navegador)
        # Vamos buscar "SESI" e "Indústria" em São Paulo
        url = "https://br.indeed.com/jobs"
        params = {"q": "SESI SENAI", "l": "São Paulo", "sort": "date"}
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

        print(f"🛰️ Acessando Indeed...")
        response = requests.get(url, params=params, headers=headers)
        
        if response.status_code != 200:
            print(f"❌ Erro no Indeed: {response.status_code}")
            return

        # 3. "Garimpar" as vagas no HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        vagas_html = soup.find_all('div', class_='job_seen_beacon') # Bloco padrão de vaga do Indeed

        print(f"📦 Encontradas {len(vagas_html)} vagas potenciais.")

        for vaga in vagas_html:
            try:
                # Extrair os textos das tags HTML
                titulo = vaga.find('h2').text.strip() if vaga.find('h2') else "N/A"
                empresa = vaga.find('span', {'data-testid': 'company-name'}).text.strip() if vaga.find('span', {'data-testid': 'company-name'}) else "N/A"
                local = vaga.find('div', {'data-testid': 'text-location'}).text.strip() if vaga.find('div', {'data-testid': 'text-location'}) else "SP"
                link = "https://br.indeed.com" + vaga.find('a')['href'] if vaga.find('a') else ""

                # Organizar para a sua planilha (ID, Título, Empresa, Cidade, UF, Modalidade, Salário, Área, Link, Status)
                linha = [
                    "INDEED_" + str(int(time.time())), # Gera um ID único simples
                    titulo,
                    empresa,
                    local,
                    "SP",
                    "Presencial",
                    "A combinar",
                    "Indústria / Educação",
                    link,
                    "Ativa"
                ]

                sheet.append_row(linha)
                print(f"✔️ Salva: {titulo} - {empresa}")
                time.sleep(1) # Evita ser bloqueado por excesso de velocidade

            except Exception as e:
                print(f"⚠️ Pulei uma vaga por erro: {e}")

        print("🚀 SUCESSO! Verifique sua planilha e o Portal.")

    except Exception as e:
        print(f"❌ ERRO GERAL: {e}")

if __name__ == "__main__":
    minerar_indeed()
