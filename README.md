# Dashboard de Análise de Acidentes de Trânsito

Este projeto implementa um dashboard interativo para análise de dados de acidentes de trânsito utilizando Streamlit, XGBoost e integração com LLM Llama 3.1 via Ollama.

## 🚀 Funcionalidades

### Dashboard Interativo
- **Seleção de Ano:** Permite visualizar dados de acidentes por ano (2020-2025).
- **Mapa de calor de acidentes** por UF e tipo
- **Previsão de risco por horário** com gráficos de linha
- **Análise de causas principais** com gráficos de barras horizontais
- **Gráficos interativos** para acidentes por dia da semana e condições meteorológicas
- **Mapa de Densidade de Risco de Acidentes:** Visualização da densidade de acidentes com base no risco previsto.
- **Top 10 Trechos Críticos:** Tabela com os 10 trechos de rodovia com maior risco de acidentes.

### Integração com LLM
- **Llama 3.1 via Ollama** para análise contextual dos dados
- **Interface de chat** para perguntas sobre os dados
- **Respostas baseadas** no contexto dos dados carregados

## 📋 Pré-requisitos

### Python e Dependências
```bash
pip install streamlit pandas plotly xgboost scikit-learn requests ollama numpy matplotlib seaborn tqdm jupyter IPython pathlib bcrypt python-dotenv uvicorn starlette itsdangerous authlib
```

### Ollama (para LLM)
```bash
# Instalar Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Iniciar o serviço
ollama serve

# Baixar o modelo Llama 3.1
ollama pull llama3.1
```

## 🗂️ Estrutura dos Dados

O dashboard espera arquivos CSV com os seguintes padrões de nome e colunas principais:

- **Arquivos de Acidentes:** `acidentesYYYY_todas_causas_tipos.csv` (onde YYYY é o ano)
- **Arquivos DataTran:** `datatranYYYY.csv` (onde YYYY é o ano)

**Colunas principais esperadas:**
- `data_inversa`: Data do acidente
- `horario`: Hora do acidente
- `uf`: Unidade Federativa
- `km`: Quilômetro da rodovia
- `causa_acidente`: Causa do acidente
- `tipo_acidente`: Tipo do acidente
- `classificacao_acidente`: Classificação (com/sem vítimas)
- `condicao_metereologica`: Condições climáticas
- `tipo_pista`: Tipo da pista
- `dia_semana`: Dia da semana
- `latitude`: Latitude do acidente (formato com vírgula ou ponto)
- `longitude`: Longitude do acidente (formato com vírgula ou ponto)

## 🚀 Como Executar (Windows)

### 1. Organizar os Dados
Crie uma pasta chamada `upload` no mesmo diretório do `app_optimized.py` e coloque todos os arquivos CSV fornecidos dentro dela.

### 2. Instalar Dependências
Abra o Prompt de Comando (CMD) ou PowerShell no diretório do projeto e execute:
```cmd
pip install -r requirements.txt
```

### 3. Executar o Dashboard
No mesmo Prompt de Comando (CMD) ou PowerShell, execute:
```cmd
streamlit run app_optimized.py 
```

### 4. Acessar no Navegador
Abra seu navegador e acesse:
```
http://localhost:8501
```

## 📊 Features do Dashboard

### 1. Visualizações Principais
- **Mapa de Calor:** Distribuição de acidentes por UF e tipo
- **Gráfico de Linha:** Risco de acidentes por horário do dia
- **Gráfico de Barras:** Top 10 causas de acidentes
- **Gráfico Pizza:** Distribuição por dia da semana
- **Gráfico de Barras:** Acidentes por condição meteorológica

### 2. Chat com LLM
- **Interface de texto** para perguntas
- **Contexto dos dados** fornecido automaticamente
- **Respostas baseadas** nos dados analisados

## 🔧 Configurações

### Arquivos de Dados
Os arquivos CSV devem estar na pasta `upload` no mesmo diretório do `app_optimized.py`.

## 📈 Métricas e KPIs

- **Total de Registros:** Número de acidentes analisados
- **AUC-ROC Score:** Performance do modelo de classificação
- **Acurácia:** Precisão das predições
- **Importância das Features:** Quais variáveis mais influenciam o risco

### Problema: Dados não carregam
**Solução:** Verificar se os arquivos CSV estão na pasta `upload` e se o encoding está correto (`encoding=\'latin1\'`).
