import requests
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os

def conectar_planilha():
    # Escopos para Google Sheets e Drive
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    
    # O arquivo credentials.json é criado pelo GitHub Actions usando o seu SECRET
    creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
    client = gspread.authorize(creds)
    
    # --- INSIRA O ID DA SUA PLANILHA ABAIXO ---
    spreadsheet_id = "COLOQUE_AQUI_O_ID_DA_SUA_PLANILHA" 
    
    # Abre a primeira aba da planilha
    return client.open_by_key(spreadsheet_id).sheet1

def minerar_e_salvar():
    url = "https://sesisenaisp.empregare.com/api/v1/vacancies/search"
    params = {"page": 1, "limit": 20, "sorting": "newest"}

    print("🛰️ Iniciando mineração automática no SESI SENAI SP...")
    
    try:
        # 1. PEGA OS DADOS DO SESI
        response = requests.get(url, params=params)
        vagas_brutas = response.json().get('data', [])
        
        # 2. CONECTA NA PLANILHA
        sheet = conectar_planilha()
        print(f"✅ Conectado à planilha. Enviando {len(vagas_brutas)} vagas...")

        # 3. ENVIA LINHA POR LINHA
        for vaga in vagas_brutas:
            nova_linha = [
                vaga.get('id'),                      # Coluna ID
                vaga.get('title'),                   # Coluna Título
                "SESI/SENAI SP",                     # Coluna Empresa
                vaga.get('city', {}).get('name'),    # Coluna Cidade
                "SP",                                # Coluna UF
                "Presencial",                        # Coluna Tipo
                "A combinar",                        # Coluna Salário
                vaga.get('area', {}).get('name'),    # Coluna Área
                f"https://sesisenaisp.empregare.com/pt-br/vaga/{vaga.get('id')}", # Link
                "Ativa"                              # Coluna Status
            ]
            # Adiciona a linha no final da planilha
            sheet.append_row(nova_linha)
            
        print("🚀 Sucesso! As vagas já devem estar na sua Planilha Google.")

    except Exception as e:
        print(f"❌ Erro no processo: {e}")

if __name__ == "__main__":
    minerar_e_salvar()
