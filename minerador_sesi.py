import requests
import pandas as pd

def minerar_sesi_senai():
    # URL da API interna da Empregare (SESI/SENAI SP)
    url = "https://sesisenaisp.empregare.com/api/v1/vacancies/search"
    
    # Parâmetros de busca (podemos ajustar para pegar mais páginas)
    params = {
        "page": 1,
        "limit": 50,
        "sorting": "newest"
    }

    print("🛰️ Iniciando mineração no SESI SENAI SP...")
    
    try:
        response = requests.get(url, params=params)
        data = response.json()
        vagas_brutas = data.get('data', [])
        
        lista_vagas = []
        for vaga in vagas_brutas:
            lista_vagas.append({
                "Título": vaga.get('title'),
                "Empresa": "SESI/SENAI SP",
                "Cidade": vaga.get('city', {}).get('name', 'São Paulo'),
                "UF": "SP",
                "Tipo": "Presencial", # Padronização SESI
                "Salário": 0, # Geralmente a combinar
                "Área": vaga.get('area', {}).get('name', 'Educação/Indústria'),
                "Link_Inscrição": f"https://sesisenaisp.empregare.com/pt-br/vaga/{vaga.get('id')}",
                "Status": "Ativa"
            })
            
        df = pd.DataFrame(lista_vagas)
        print(f"✅ Sucesso! {len(df)} vagas encontradas.")
        return df

    except Exception as e:
        print(f"❌ Erro na mineração: {e}")
        return pd.DataFrame()

# Executar e salvar para você copiar para a planilha
df_sesi = minerar_sesi_senai()
if not df_sesi.empty:
    df_sesi.to_csv("vagas_sesi_senai.csv", index=False, encoding='utf-8-sig')
    print("📂 Arquivo 'vagas_sesi_senai.csv' gerado. Agora é só copiar para sua Planilha Google!")
