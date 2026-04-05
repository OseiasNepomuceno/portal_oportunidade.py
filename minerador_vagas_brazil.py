import pandas as pd
import requests
from datetime import datetime, timedelta
from streamlit_gsheets import GSheetsConnection
import streamlit as st

# --- CONFIGURAÇÕES ---
DIAS_LIMITE = 30

def carregar_dados_existentes():
    try:
        # Usamos ttl=0 para garantir que o minerador sempre veja a versão mais recente da planilha
        conn = st.connection("gsheets", type=GSheetsConnection)
        df = conn.read(ttl=0)
        return df.dropna(how="all")
    except:
        return pd.DataFrame()

def minerar_vagas_novas():
    vagas_novas = []
    hoje = datetime.now().strftime("%Y-%m-%d")

    # 1. CAPTURA ADZUNA
    try:
        aid, akey = st.secrets["APP_ID"], st.secrets["APP_KEY"]
        url = f"https://api.adzuna.com/v1/api/jobs/br/search/1?app_id={aid}&app_key={akey}&results_per_page=50&what=industria%20tecnologia"
        res = requests.get(url).json()
        for item in res.get('results', []):
            vagas_novas.append({
                "Título": item.get('title'),
                "Empresa": item.get('company', {}).get('display_name', 'Confidencial'),
                "Cidade": item.get('location', {}).get('display_name', 'Brasil'),
                "UF": "BR",
                "Tipo": "Remoto" if "remoto" in item.get('description', '').lower() else "Presencial",
                "Salário": item.get('salary_min', 0),
                "Fonte": "Adzuna",
                "Área": "Geral",
                "Link_Inscrição": item.get('redirect_url'),
                "Status": "Ativa",
                "Data_Captura": hoje
            })
    except Exception as e:
        print(f"Erro Adzuna: {e}")

    # 2. CAPTURA GOOGLE JOBS (SerpApi)
    try:
        serp_key = st.secrets["SERPAPI_KEY"]
        url_serp = f"https://serpapi.com/search.json?engine=google_jobs&q=vagas+industria+brasil&hl=pt&gl=br&api_key={serp_key}"
        res_serp = requests.get(url_serp).json()
        for item in res_serp.get('jobs_results', []):
            loc = item.get('location', 'Brasil')
            uf_extraida = "BR"
            if "," in loc:
                possivel_uf = loc.split(",")[-1].strip().upper()
                if len(possivel_uf) == 2:
                    uf_extraida = possivel_uf

            vagas_novas.append({
                "Título": item.get('title'),
                "Empresa": item.get('company_name'),
                "Cidade": loc,
                "UF": uf_extraida,
                "Tipo": "Ver na Fonte",
                "Salário": 0,
                "Fonte": "Google",
                "Área": "Geral",
                "Link_Inscrição": item.get('share_link'),
                "Status": "Ativa",
                "Data_Captura": hoje
            })
    except Exception as e:
        print(f"Erro Google Jobs: {e}")

    return pd.DataFrame(vagas_novas)

def atualizar_planilha():
    df_antigo = carregar_dados_existentes()
    df_novas = minerar_vagas_novas()
    
    # 1. Unir e remover duplicatas baseadas no LINK
    if not df_antigo.empty:
        # Garante que Link_Inscrição seja string para comparar
        df_antigo['Link_Inscrição'] = df_antigo['Link_Inscrição'].astype(str)
        df_novas['Link_Inscrição'] = df_novas['Link_Inscrição'].astype(str)
        
        df_total = pd.concat([df_antigo, df_novas]).drop_duplicates(subset=['Link_Inscrição'], keep='first')
    else:
        df_total = df_novas

    if df_total.empty:
        print("Nenhuma vaga encontrada para atualizar.")
        return

    # 2. LIMPEZA: Manter apenas os últimos 30 dias
    df_total['Data_Captura'] = pd.to_datetime(df_total['Data_Captura'])
    data_corte = datetime.now() - timedelta(days=DIAS_LIMITE)
    df_total = df_total[df_total['Data_Captura'] >= data_corte]
    
    # 3. Formatação Final
    df_total = df_total.sort_values(by='Data_Captura', ascending=False)
    df_total['Data_Captura'] = df_total['Data_Captura'].dt.strftime("%Y-%m-%d")
    
    # 4. Gerar IDs sequenciais
    df_total['ID'] = range(1, len(df_total) + 1)

    # 5. Organizar colunas na ordem exata da sua planilha (12 colunas)
    colunas_ordenadas = [
        "ID", "Título", "Empresa", "Cidade", "UF", "Tipo", 
        "Salário", "Fonte", "Área", "Link_Inscrição", "Status", "Data_Captura"
    ]
    df_total = df_total[colunas_ordenadas]

    # --- COMANDO DE SALVAMENTO ---
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        conn.update(data=df_total)
        print(f"✅ Sucesso! Planilha atualizada com {len(df_total)} vagas.")
    except Exception as e:
        print(f"❌ Erro ao salvar na planilha: {e}")
    
    return df_total

if __name__ == "__main__":
    atualizar_planilha()
