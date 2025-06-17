import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score
import numpy as np
import os

st.set_page_config(page_title="Dashboard de Acidentes de Trânsito", layout="wide")
@st.cache_data
def load_data(selected_year):
    all_data = []
    base_upload_path = "upload"
    file_names = {
        "acidentes": f"acidentes{selected_year}_todas_causas_tipos.csv",
        "datatran": f"datatran{selected_year}.csv"
    }
    for key, file_name in file_names.items():
        file_path = os.path.join(base_upload_path, file_name)
        try:
            df = pd.read_csv(file_path, sep=";", encoding="latin1")
            all_data.append(df)
        except FileNotFoundError:
            st.warning(f"Arquivo {file_path} não encontrado. Pulando...")
        except Exception as e:
            st.error(f"Erro ao carregar {file_path}: {e}")
    return pd.concat(all_data, ignore_index=True) if all_data else pd.DataFrame()

# Função para carregar dados do IBGE
@st.cache_data
def load_ibge_data():
    file_path = os.path.join("upload", "ibge_agregados_list.csv")
    try:
        df_ibge = pd.read_csv(file_path, sep=";", encoding="utf-8")
        return df_ibge
    except FileNotFoundError:
        st.warning(f"Arquivo {file_path} não encontrado.")
    except Exception as e:
        st.error(f"Erro ao carregar {file_path}: {e}")
    return pd.DataFrame()

# Título principal
st.title("🚗 Dashboard de Análise de Acidentes de Trânsito")
st.markdown("---")

# Seleção do Ano
current_year = 2023
available_years = [2020, 2021, 2022, 2023, 2024, 2025]
selected_year = st.sidebar.selectbox(
    "Selecione o Ano dos Dados",
    available_years,
    index=available_years.index(current_year)
)

df = load_data(selected_year)

if df.empty:
    st.error("❌ Não foi possível carregar os dados. Verifique os arquivos CSV.")
else:
    # Sidebar com informações
    st.sidebar.header("📊 Informações dos Dados")
    st.sidebar.metric("Total de Registros", len(df))
    st.sidebar.metric("Ano Selecionado", selected_year)

    # Limpeza básica
    df.columns = df.columns.str.lower()
    if "data_inversa" in df.columns:
        df["data_inversa"] = pd.to_datetime(df["data_inversa"], errors="coerce")
        df["ano"] = df["data_inversa"].dt.year
        df["mes"] = df["data_inversa"].dt.month
        df["dia_semana_num"] = df["data_inversa"].dt.dayofweek
    if "horario" in df.columns:
        df["hora"] = pd.to_datetime(df["horario"], format="%H:%M:%S", errors="coerce").dt.hour
    for col in ["km", "pessoas", "mortos", "feridos", "veiculos"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
    if "latitude" in df.columns and "longitude" in df.columns:
        df["latitude"] = df["latitude"].str.replace(",", ".").astype(float)
        df["longitude"] = df["longitude"].str.replace(",", ".").astype(float)
    else:
        st.warning("Colunas 'latitude' ou 'longitude' não encontradas. O mapa de calor pode não funcionar.")

    # Layout de gráficos
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🔥 Mapa de Calor: Acidentes por UF e Tipo")
        if "uf" in df.columns and "tipo_acidente" in df.columns:
            heatmap_data = df.groupby(["uf", "tipo_acidente"]).size().unstack(fill_value=0)
            fig_heatmap = px.imshow(
                heatmap_data,
                text_auto=True,
                aspect="auto",
                color_continuous_scale="Reds",
                title="Distribuição de Acidentes por UF e Tipo"
            )
            fig_heatmap.update_layout(height=400)
            st.plotly_chart(fig_heatmap, use_container_width=True)
    with col2:
        st.subheader("⏰ Risco de Acidentes por Horário")
        if "hora" in df.columns:
            risk_by_hour = df.groupby("hora").size().reset_index(name="acidentes")
            fig_risk = px.line(
                risk_by_hour,
                x="hora",
                y="acidentes",
                title="Número de Acidentes por Hora do Dia",
                markers=True
            )
            fig_risk.update_traces(line_color="#ff6b6b")
            fig_risk.update_layout(height=400)
            st.plotly_chart(fig_risk, use_container_width=True)

    st.subheader("📈 Principais Causas de Acidentes")
    if "causa_acidente" in df.columns:
        top_causes = df["causa_acidente"].value_counts().head(10)
        fig_causes = px.bar(
            x=top_causes.values,
            y=top_causes.index,
            orientation="h",
            title="Top 10 Causas de Acidentes",
            color=top_causes.values,
            color_continuous_scale="viridis"
        )
        fig_causes.update_layout(height=500)
        st.plotly_chart(fig_causes, use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        if "dia_semana" in df.columns:
            st.subheader("📅 Acidentes por Dia da Semana")
            day_counts = df["dia_semana"].value_counts()
            fig_days = px.pie(
                values=day_counts.values,
                names=day_counts.index,
                title="Distribuição por Dia da Semana"
            )
            st.plotly_chart(fig_days, use_container_width=True)
    with col4:
        if "condicao_metereologica" in df.columns:
            st.subheader("🌤️ Condições Meteorológicas")
            weather_counts = df["condicao_metereologica"].value_counts().head(8)
            fig_weather = px.bar(
                x=weather_counts.index,
                y=weather_counts.values,
                title="Acidentes por Condição Meteorológica"
            )
            fig_weather.update_xaxes(tickangle=45)
            st.plotly_chart(fig_weather, use_container_width=True)

    st.markdown("---")
    st.header("🗺️ Mapa de Densidade de Risco de Acidentes")
    if "latitude" in df.columns and "longitude" in df.columns:
        if "risco" not in df.columns:
            df["risco"] = df.groupby(["latitude", "longitude"])["latitude"].transform("count")
        df_map = df[df["risco"] > 0]
        if not df_map.empty:
            fig_density_map = px.density_mapbox(
                df_map,
                lat="latitude",
                lon="longitude",
                z="risco",
                radius=10,
                center=dict(lat=-14.235, lon=-51.925),
                zoom=3,
                mapbox_style="open-street-map",
                title="Mapa de Densidade de Risco de Acidentes"
            )
            fig_density_map.update_layout(height=600)
            st.plotly_chart(fig_density_map, use_container_width=True)

            st.subheader("🔝 Top 10 Trechos Críticos (por Risco)")
            top_10_risco = df_map.nlargest(10, "risco")
            if not top_10_risco.empty:
                st.dataframe(top_10_risco[["latitude", "longitude", "risco", "uf", "br", "km"]])
            else:
                st.info("Nenhum trecho com risco significativo encontrado.")
        else:
            st.info("Nenhum dado com risco > 0 para exibir.")
    else:
        st.warning("Colunas 'latitude' ou 'longitude' não disponíveis para o mapa de densidade.")

    st.markdown("---")
    st.header("🧠 Pergunte ao chat")
    st.info("Para usar integração com Ollama, instale e inicie o serviço, etc.")
    user_question = st.text_area(
        "Faça uma pergunta sobre os dados de acidentes:",
        "Quais são os principais fatores de risco para acidentes de trânsito?"
    )
    if st.button("🤖 Perguntar à LLM"):
        try:
            import ollama
            data_context = f"Dados de acidentes: Total={len(df)}"
            prompt = f"{data_context}\nPergunta: {user_question}"
            response = ollama.chat(
                model="llama3.1",
                messages=[{"role": "user", "content": prompt}]
            )
            st.success("Resposta da LLM:")
            st.write(response["message"]["content"])
        except Exception as e:
            st.error(f"Erro ao conectar com Ollama: {e}")

    st.header("📊 Dados Complementares: IBGE")
    ibge_df = load_ibge_data()
    if not ibge_df.empty:
        st.success("Dados do IBGE carregados com sucesso!")
        st.dataframe(ibge_df.head(80))
        st.download_button(
            label="📥 Baixar Dados Completos do IBGE",
            data=ibge_df.to_csv(index=False).encode("utf-8"),
            file_name="ibge_agregados_list.csv",
            mime="text/csv"
        )
    else:
        st.info("Nenhum dado do IBGE foi carregado.")
        

def logout():
    st.session_state.clear()
    st.switch_page(".\pages\login.py")

with st.sidebar:
    if st.button("Sair"): 
        logout()

    st.markdown("---")
    st.markdown("**Dashboard desenvolvido por Arthur Pedro e Pedro Lacerda** 🤓🚀")
