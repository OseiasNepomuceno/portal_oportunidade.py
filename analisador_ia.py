import google.generativeai as genai
import os

# Configuração da Chave (Pega do seu ambiente ou variável)
genai.configure(api_key="SUA_CHAVE_AQUI")

def estruturar_curriculo_ia(texto_antigo, novas_infos, vaga_objetivo="Geral"):
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    # O PROMPT MESTRE (AQUELE QUE ESTRUTURAMOS)
    prompt = f"""
    Atue como um Especialista em Recrutamento e Seleção sênior, mestre nos frameworks STAR, WHO e ELITE.
    
    TAREFA:
    Reescrever as experiências profissionais e educacionais baseando-se nos dados abaixo.
    
    DADOS DO CURRÍCULO ATUAL:
    {texto_antigo}
    
    NOVAS ATUALIZAÇÕES DO USUÁRIO:
    {novas_infos}
    
    VAGA DE INTERESSE (OPCIONAL):
    {vaga_objetivo}
    
    REGRAS DE OURO:
    1. Framework STAR: Para cada experiência, foque na Ação (o que foi feito tecnicamente) e no Resultado (números, % de ganho, economia de tempo).
    2. Verbos de Ação: Inicie as frases com verbos fortes (Ex: "Desenvolvi", "Liderei", "Otimizei").
    3. Adapte o currículo para a VAGA DE INTERESSE, priorizando habilidades que o recrutador busca.
    4. Formate a saída de forma limpa, com Títulos Claros para cada seção.
    """
    
    response = model.generate_content(prompt)
    return response.text
