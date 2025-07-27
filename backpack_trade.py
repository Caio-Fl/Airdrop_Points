import os
import time
import requests
import pandas as pd
import streamlit as st
import plotly.graph_objects as go

def intervalo_para_minutos(intervalo):
    if intervalo.endswith("m"):
        return int(intervalo.replace("m", ""))
    elif intervalo.endswith("h"):
        return int(intervalo.replace("h", "")) * 60
    elif intervalo.endswith("d"):
        return int(intervalo.replace("d", "")) * 1440
    else:
        return None
# Configuração da página
st.set_page_config(page_title="EMA Trade Bot", layout="wide")

# Parâmetros globais
NUMERO = os.getenv("NUMERO_WHATSAPP", "SEU_NUMERO")
APIKEY = os.getenv("APIKEY_WHATSAPP", "SUA_API_KEY")
enviar_whatsapp = True
pasta_graficos = "graficos"

# Placeholder de sessão para logs e gráficos
if "placeholder_log" not in st.session_state:
    st.session_state.placeholder_log = st.empty()
if "placeholder_chart" not in st.session_state:
    st.session_state.placeholder_chart = st.empty()
if "csv_logs" not in st.session_state:
    st.session_state.csv_logs = []

# Função para carregar e processar os dados do símbolo
@st.cache_data(show_spinner=False)
def carregar_dados(symbol: str, interval: str):
    # Substitua por sua lógica real de carregamento de dados
    df = pd.read_csv(f"data/{symbol}_{interval}.csv")
    return df

# Parâmetros do símbolo e intervalo
symbol = st.sidebar.selectbox("Escolha o símbolo:", ["BTCUSDT", "ETHUSDT", "BNBUSDT"])
interval = st.sidebar.selectbox("Escolha o intervalo:", ["1m", "5m", "15m", "1h"])

# Carregar os dados
try:
    df = carregar_dados(symbol, interval)
except Exception as e:
    st.error(f"Erro ao carregar dados: {e}")
    st.stop()

# Exemplo de dados mockados (substitua pelos valores reais extraídos do df)
ema_periods = {"1m": [21, 50, 100, 200], "5m": [21, 50, 100, 200], "15m": [21, 50, 100, 200], "1h": [21, 50, 100, 200]}
ema21, ema50, ema100, ema200 = 101.2, 102.0, 103.5, 105.0
delta21, delta50, delta100, delta200 = 0.2, 0.3, 0.25, 0.15
vol_last, vol_medio = 320.0, 290.0
last10_bull_volumes = pd.Series([20.0, 18.0, 25.0, 30.0, 28.0, 15.0, 22.0, 19.0, 23.0, 21.0])
last10_bear_volumes = pd.Series([15.0, 13.0, 12.0, 10.0, 11.0, 9.0, 14.0, 8.0, 10.0, 7.0])
touched_ema21 = touched_ema50 = touched_ema100 = touched_ema200 = False
price = 102.5
preco_entrada, stop_loss, take_profit = 102.3, 101.0, 104.0
sinal = "BUY Signal"
motivo = "Cross EMA 21 > 50"

# Mostrar gráfico
fig = go.Figure()
fig.add_trace(go.Candlestick(
    x=df["start"], open=df["open"], high=df["high"],
    low=df["low"], close=df["close"], name="Price"
))
for period in ema_periods[interval]:
    colname = f"EMA_{period}"
    if colname in df.columns:
        fig.add_trace(go.Scatter(
            x=df["start"], y=df[colname],
            mode="lines", name=colname
        ))

# Bollinger Bands
if "BB_Upper" in df.columns and "BB_Lower" in df.columns:
    fig.add_trace(go.Scatter(
        x=df["start"], y=df["BB_Upper"],
        line=dict(color='rgba(255, 215, 0, 0.3)'),
        name='BB Upper'
    ))
    fig.add_trace(go.Scatter(
        x=df["start"], y=df["BB_Lower"],
        line=dict(color='rgba(255, 215, 0, 0.3)'),
        name='BB Lower'
    ))

# Volume Bars
if "volume" in df.columns:
    fig.add_trace(go.Bar(
        x=df["start"], y=df["volume"], name="Volume",
        marker=dict(color='rgba(150, 150, 150, 0.3)'), yaxis='y2'
    ))
fig.update_layout(
    title=f"{symbol} - {interval}",
    template="plotly_dark", height=700,
    yaxis=dict(title="Price (USD)", domain=[0.25, 1]),
    yaxis2=dict(title="Volume", domain=[0, 0.20], side='right', showgrid=False)
)
st.session_state.placeholder_chart.plotly_chart(fig, use_container_width=True, key=f"chart_{symbol}")

# Salvar imagem se houver sinal
if ("BUY" in sinal) or ("SELL" in sinal):
    if not os.path.exists(pasta_graficos):
        os.makedirs(pasta_graficos)
    fig_filename = f"grafico_{symbol}_{interval}_{int(time.time())}.png"
    fig_path = os.path.join(pasta_graficos, fig_filename)
    try:
        fig.write_image(fig_path, format="png")
    except Exception as e:
        st.session_state.placeholder_log.warning(f"⚠ Não foi possível salvar o gráfico: {e}")

# LOG DE ANÁLISE
log_text = ""
tendency, reason = "", ""
if ema21 and ema50 and ema100 and ema200:
    if ema200 > ema100 > ema50 > ema21:
        tendency = "📉 All EMAs aligned downward"
        reason = "Strong bearish trend, just think about selling/short signals!"
    elif ema21 > ema50 > ema100 > ema200:
        tendency = "📈 All EMAs aligned upward"
        reason = "Strong bullish trend, just think about buying/long signals!"
    elif ema200 < ema100 > ema50 and ema100 > ema21:
        tendency = "⚠️ Possible reversal: EMA_100 > EMA_50, but EMA_50 < EMA_21"
        reason = "Short-term reversal"
    log_text = (
        f"📊 Last Price: {price:.5f}"
        f"\n➡️ EMA_21: {ema21:.5f} | Δ%: {delta21:.3f}"
        f"\n➡️ EMA_50: {ema50:.5f} | Δ%: {delta50:.3f}"
        f"\n➡️ EMA_100: {ema100:.5f} | Δ%: {delta100:.3f}"
        f"\n➡️ EMA_200: {ema200:.5f} | Δ%: {delta200:.3f}"
        f"\n📦 Last Candle Volume: {vol_last:.2f} | Average Volume: {vol_medio:.2f}"
        f"\n📦 Last 10 Buying Candle Volume: {last10_bull_volumes.sum():.2f} | Last 10 Selling Candle Volume: {last10_bear_volumes.sum():.2f}"
        f"\n{sinal}\nTendency: {tendency}\nNote: {reason}"
    )

# Verificação de toque nas EMAs
if any([touched_ema21, touched_ema50, touched_ema100, touched_ema200]):
    touched_list = []
    not_touched_list = []
    for name, touched in zip(["EMA_21", "EMA_50", "EMA_100", "EMA_200"], [touched_ema21, touched_ema50, touched_ema100, touched_ema200]):
        (touched_list if touched else not_touched_list).append(name)
    log_text += (
        f"\n\n🔍 Verification of Last 5 candles:" +
        "".join([f"\n- {ema}: {'⚠️ Already Touched' if ema in touched_list else '👍 Not Touched'}" for ema in ["EMA_21", "EMA_50", "EMA_100", "EMA_200"]]) +
        f"\nAdvice: The price already touched the {', '.join(touched_list)}, so the trade opportunity may have already passed."
        f"\n       Better wait for a stronger signal next to {', '.join(not_touched_list)}!"
    )
else:
    time_window = intervalo_para_minutos(interval) * 5
    log_text += (
        f"\n\n🔍 Verifying the Last 5 candles: The price has not touched any of the EMA's in the last {time_window} {interval[-1]}"
    )

# Sinal válido: salvar e enviar
if preco_entrada:
    log_text += (
        f"\n✅ Entry: {preco_entrada:.4f}"
        f"\n🛡 Stop Loss: {stop_loss:.4f}"
        f"\n🎯 Take Profit: {take_profit:.4f}"
    )
    st.session_state.placeholder_log.code(log_text)

    st.session_state.csv_logs.append({
        "timestamp": pd.Timestamp.now(),
        "symbol": symbol,
        "interval": interval,
        "motivo": motivo,
        "sinal": sinal,
        "preco": price,
        "entrada": preco_entrada,
        "stop_loss": stop_loss,
        "take_profit": take_profit,
        "vol_ultimo": vol_last,
        "vol_medio": vol_medio
    })
    pd.DataFrame(st.session_state.csv_logs).to_csv("sinais_log.csv", index=False)

    msg_whatsapp = (
        f"🤖 Signal detected in {symbol}!\n{sinal}\n"
        f"Entry: {preco_entrada:.2f} | Stop Loss: {stop_loss:.2f} | Take Profit: {take_profit:.2f}\n"
        f"📊 Graph Saved in: {fig_path}\n\nLog of Analysis:\n{log_text}"
    )
    if enviar_whatsapp:
        mensagem = requests.utils.quote(msg_whatsapp)
        url_whatsapp = f"https://api.callmebot.com/whatsapp.php?phone={NUMERO}&text={mensagem}&apikey={APIKEY}"
        r = requests.get(url_whatsapp)
        if r.status_code == 200:
            st.session_state.placeholder_log.code(log_text + "\n\n📩 Signal sent to WhatsApp!")
        else:
            st.session_state.placeholder_log.warning("⚠ Error while sending message to WhatsApp.")
