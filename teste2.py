import pandas as pd
import plotly.express as px
import streamlit as st

# -----------------------------
# ⚡ Configuração inicial
# -----------------------------
st.set_page_config(page_title="📊 Análise de Volume Semanal", layout="wide")
st.title("📊 Análise de Volume Total por Semana (início quinta 21h)")

# -----------------------------
# 📂 Upload do CSV
# -----------------------------
uploaded_file = st.file_uploader("Carregue o arquivo CSV", type=["csv"])

if uploaded_file is not None:
    # -----------------------------
    # 1) Leitura do CSV
    # -----------------------------
    df = pd.read_csv(uploaded_file)

    # -----------------------------
    # 2) Conversão do timestamp
    # -----------------------------
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)

    # -----------------------------
    # 3) Calcular volume (price * quantity)
    # -----------------------------
    df["volume"] = df["price"] * df["quantity"]

    # -----------------------------
    # 🔹 Seleção do token
    # -----------------------------
    if "symbol" in df.columns:
        tokens_disponiveis = df["symbol"].unique().tolist()
        token_escolhido = st.selectbox("Selecione o Token para análise", ["Todos"] + tokens_disponiveis)

        if token_escolhido != "Todos":
            df = df[df["symbol"] == token_escolhido]
    else:
        st.warning("⚠️ O arquivo não possui a coluna 'symbol'. A filtragem por token não será aplicada.")

    # -----------------------------
    # 4) Ajuste da semana (quinta 21h)
    # -----------------------------
    df["adjusted_timestamp"] = df["timestamp"] - pd.Timedelta(hours=21)

    weekly_volume = (
        df.groupby(pd.Grouper(key="adjusted_timestamp", freq="W-THU"))["volume"]
        .sum()
        .reset_index()
    )
    weekly_volume["week_start"] = weekly_volume["adjusted_timestamp"] + pd.Timedelta(hours=21)

    # -----------------------------
    # 5) Volume total acumulado
    # -----------------------------
    total_volume = weekly_volume["volume"].sum()

    # -----------------------------
    # 6) Mostrar resultados
    # -----------------------------
    st.subheader("📊 Volume por Semana")
    st.dataframe(weekly_volume[["week_start", "volume"]])

    st.metric(label="🔹 Volume Total Acumulado", value=f"{total_volume:,.2f}")

    # -----------------------------
    # 7) Gráfico interativo Plotly
    # -----------------------------
    fig = px.bar(
        weekly_volume,
        x="week_start",
        y="volume",
        title=f"Volume total por semana (início quinta 21h) - {token_escolhido}",
        labels={"week_start": "Semana", "volume": "Volume"},
        text_auto=".2s",
    )

    fig.update_traces(marker_color="skyblue", marker_line_color="black", marker_line_width=1.2)
    fig.update_layout(
        width=900, height=350,  # tamanho compacto
        margin=dict(l=40, r=40, t=40, b=40),
        title_x=0.5  # centraliza título
    )

    st.plotly_chart(fig, use_container_width=False)

else:
    st.info("📥 Por favor, carregue um arquivo CSV para iniciar a análise.")
