#!/usr/bin/env python3
"""
Exemplo de integração com Ollama e Llama 3.1
Este script demonstra como usar a LLM para análise de dados de acidentes
"""

import ollama
import pandas as pd
import json

def load_sample_data():
    """Carrega dados de exemplo para demonstração"""
    try:
        df = pd.read_csv('/home/ubuntu/upload/datatran2023.csv', sep=';', encoding='latin1')
        return df.head(100)  # Amostra pequena para exemplo
    except Exception as e:
        print(f"Erro ao carregar dados: {e}")
        return pd.DataFrame()

def analyze_with_llm(data_summary, question):
    """
    Analisa dados usando Llama 3.1 via Ollama
    
    Args:
        data_summary (str): Resumo dos dados
        question (str): Pergunta a ser respondida
    
    Returns:
        str: Resposta da LLM
    """
    try:
        prompt = f"""
        Você é um especialista em análise de dados de trânsito e segurança viária.
        
        Dados disponíveis:
        {data_summary}
        
        Pergunta: {question}
        
        Por favor, forneça uma análise detalhada e insights baseados nos dados apresentados.
        Seja específico e mencione padrões, tendências e recomendações práticas.
        """
        
        response = ollama.chat(
            model='llama3.1',
            messages=[
                {
                    'role': 'user',
                    'content': prompt
                }
            ]
        )
        
        return response['message']['content']
        
    except Exception as e:
        return f"Erro ao conectar com Ollama: {e}"

def generate_data_summary(df):
    """Gera um resumo dos dados para a LLM"""
    if df.empty:
        return "Nenhum dado disponível"
    
    summary = {
        "total_registros": len(df),
        "periodo": "2023 (amostra)",
        "principais_causas": df['causa_acidente'].value_counts().head(5).to_dict() if 'causa_acidente' in df.columns else {},
        "ufs_com_mais_acidentes": df['uf'].value_counts().head(5).to_dict() if 'uf' in df.columns else {},
        "tipos_acidente": df['tipo_acidente'].value_counts().to_dict() if 'tipo_acidente' in df.columns else {},
        "condicoes_meteorologicas": df['condicao_metereologica'].value_counts().to_dict() if 'condicao_metereologica' in df.columns else {}
    }
    
    return json.dumps(summary, indent=2, ensure_ascii=False)

def main():
    """Função principal do exemplo"""
    print("🚗 Exemplo de Análise de Acidentes com Llama 3.1")
    print("=" * 50)
    
    # Carregar dados
    print("📊 Carregando dados...")
    df = load_sample_data()
    
    if df.empty:
        print("❌ Não foi possível carregar os dados.")
        return
    
    # Gerar resumo dos dados
    data_summary = generate_data_summary(df)
    print(f"✅ Dados carregados: {len(df)} registros")
    print("\n📋 Resumo dos dados:")
    print(data_summary)
    
    # Perguntas de exemplo
    questions = [
        "Quais são os principais fatores de risco para acidentes de trânsito baseado nos dados?",
        "Em que horários do dia ocorrem mais acidentes e por quê?",
        "Quais condições meteorológicas são mais perigosas para dirigir?",
        "Que recomendações você daria para reduzir acidentes de trânsito?",
        "Existe algum padrão nos tipos de acidentes por estado?"
    ]
    
    print("\n🤖 Análises com Llama 3.1:")
    print("=" * 50)
    
    for i, question in enumerate(questions, 1):
        print(f"\n{i}. {question}")
        print("-" * 60)
        
        response = analyze_with_llm(data_summary, question)
        print(response)
        print("\n" + "="*60)

def interactive_mode():
    """Modo interativo para perguntas personalizadas"""
    print("\n🔄 Modo Interativo")
    print("Digite suas perguntas (ou 'sair' para terminar):")
    
    df = load_sample_data()
    if df.empty:
        print("❌ Não foi possível carregar os dados.")
        return
    
    data_summary = generate_data_summary(df)
    
    while True:
        question = input("\n❓ Sua pergunta: ").strip()
        
        if question.lower() in ['sair', 'exit', 'quit']:
            print("👋 Até logo!")
            break
        
        if not question:
            continue
        
        print("\n🤖 Analisando...")
        response = analyze_with_llm(data_summary, question)
        print(f"\n💡 Resposta:\n{response}")

if __name__ == "__main__":
    try:
        # Verificar se Ollama está disponível
        ollama.list()
        print("✅ Ollama conectado com sucesso!")
        
        # Executar análises automáticas
        main()
        
        # Modo interativo
        interactive_mode()
        
    except Exception as e:
        print(f"❌ Erro ao conectar com Ollama: {e}")
        print("\n📝 Instruções para configurar Ollama:")
        print("1. Instalar: curl -fsSL https://ollama.ai/install.sh | sh")
        print("2. Iniciar: ollama serve")
        print("3. Baixar modelo: ollama pull llama3.1")

