import streamlit as st
import requests
import time
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from scipy.signal import find_peaks

# ==== Funções ====

def detectar_pivots(df, window=2, distancia_minima=3):
    """
    Detecta pivots de alta e baixa após suavizar preços com média móvel simples.

    Retorna índices dos pivots de alta (máximos locais) e baixa (mínimos locais),
    e também as séries suavizadas (high_smooth, low_smooth).
    """
    high_smooth = df['high'].rolling(window=window, center=True).mean()
    low_smooth = df['low'].rolling(window=window, center=True).mean()

    high_smooth_clean = high_smooth.dropna()
    low_smooth_clean = low_smooth.dropna()

    peaks, _ = find_peaks(high_smooth_clean, distance=distancia_minima)
    valleys, _ = find_peaks(-low_smooth_clean, distance=distancia_minima)

    offset = 0 #(window - 1) // 2

    indices_pivots_alta = peaks + offset
    indices_pivots_baixa = valleys + offset

    return indices_pivots_alta.tolist(), indices_pivots_baixa.tolist(), indices_pivots_alta, indices_pivots_baixa

def obter_ultimo_pivot(df, window=2, distancia_minima=3):
    _,_,indices_alta, indices_baixa = detectar_pivots(df, window=window, distancia_minima=distancia_minima)
    n = len(df)

    if len(indices_alta) == 0 and len(indices_baixa) == 0:
        return min(6, n)  # fallback

    ultimo_pivot = max(
        indices_alta.max() if len(indices_alta) > 0 else 0,
        indices_baixa.max() if len(indices_baixa) > 0 else 0
    )
    return n - ultimo_pivot

def detectar_tendencia_simples(df, n):
    mids = ((df['high'] + df['low']) / 2).iloc[-n:]
    is_rising = all(x <= y for x, y in zip(mids, mids[1:]))
    is_falling = all(x >= y for x, y in zip(mids, mids[1:]))
    equals = sum(1 for x, y in zip(mids, mids[1:]) if x == y)
    if is_rising and equals < 2:
        return "rising"
    elif is_falling and equals < 2:
        return "falling"
    else:
        return "lateral"

def detectar_tendencia_regressao(df, n=5, tolerancia=0.1):
    # Usar ponto médio em vez do close
    mids = ((df['high'] + df['low']) / 2).iloc[-n:]
    x = list(range(len(mids)))
    y = mids.values

    # Regressão linear simples
    a = (n * sum(x[i] * y[i] for i in range(n)) - sum(x) * sum(y)) / \
        (n * sum(x[i]**2 for i in range(n)) - sum(x)**2)
    b = (sum(y) - a * sum(x)) / n  # intercepto (não usado, mas mantido)

    # Variação percentual do início ao fim
    variacao_pct = (mids.iloc[-1] - mids.iloc[0]) / mids.iloc[0] * 100

    if variacao_pct > tolerancia:
        return "rising"
    elif variacao_pct < -tolerancia:
        return "falling"
    else:
        return "lateral"

def calcular_trade_levels(df, preco_entrada, p=0.02, tipo='SELL', risk_reward_ratio=2):
    """
    Calcula níveis de Stop Loss e Take Profit com base no preço de entrada,
    pivots e fator de risco/recompensa. Retorna também os percentuais relativos.

    Parâmetros:
        df: DataFrame com colunas ['high', 'low', 'close']
        preco_entrada: float, preço de entrada da operação
        p: float, margem percentual acima/abaixo do pivot para definir o stop loss
        tipo: str, 'BUY' ou 'SELL'
        risk_reward_ratio: float, fator multiplicador do risco para definir take profit

    Retorna:
        dict com preço de entrada, stop loss, take profit, percentuais e pivot
    """
    p = p/100
    pivots_alta, pivots_baixa,_,_ = detectar_pivots(df, window=1, distancia_minima=3)

    if tipo == 'SELL':
        pivots_validos = [i for i in pivots_alta if df.loc[i, 'high'] > preco_entrada]
        pivots_contrario = [i for i in pivots_baixa if df.loc[i, 'low'] < preco_entrada]
        if not pivots_validos:
            return None
        if not pivots_contrario:
            return None
        pivot1_idx = pivots_contrario[-1]
        print(pivots_contrario)
        pivot2_idx = pivots_validos[-1]
        max_pivot = df.loc[pivot2_idx, 'high']
        stop_loss = max_pivot * (1 + p)
        risco = abs(preco_entrada - stop_loss)
        take_profit = preco_entrada - risk_reward_ratio * risco

    elif tipo == 'BUY':
        pivots_validos = [i for i in pivots_baixa if df.loc[i, 'low'] < preco_entrada]
        pivots_contrario = [i for i in pivots_alta if df.loc[i, 'high'] > preco_entrada]
        if not pivots_validos:
            return None
        if not pivots_contrario:
            return None
        pivot1_idx = pivots_contrario[-1]
        print(pivots_contrario)
        pivot2_idx = pivots_validos[-1]
        print(pivots_validos)
        min_pivot = df.loc[pivot2_idx, 'low']
        stop_loss = min_pivot * (1 - p)
        risco = abs(preco_entrada - stop_loss)
        take_profit = preco_entrada + risk_reward_ratio * risco

    else:
        raise ValueError("Tipo de operação deve ser 'BUY' ou 'SELL'")

    stop_loss_pct = abs(stop_loss - preco_entrada) / preco_entrada * 100
    take_profit_pct = abs(take_profit - preco_entrada) / preco_entrada * 100

    return {
        'preco_entrada': preco_entrada,
        'stop_loss': stop_loss,
        'stop_loss_pct': stop_loss_pct,
        'take_profit': take_profit,
        'take_profit_pct': take_profit_pct,
        'pivot1_index': pivot1_idx,
        'pivot2_index': pivot2_idx,
        'risco_absoluto': risco,
        'risk_reward_ratio': risk_reward_ratio
    }

def obter_dados(symbol="BTC_USDC_PERP", intervalo="15m", horas=120):
    now = int(time.time())
    start_time = now - (horas * 3600)
    url = "https://api.backpack.exchange/api/v1/klines"
    params = {
        "symbol": symbol,
        "interval": intervalo,
        "startTime": start_time,
        "endTime": now,
        "klinePriceType": "LastPrice"
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    klines = response.json()
    df = pd.DataFrame(klines)
    df["start"] = pd.to_datetime(df["start"])
    df["open"] = pd.to_numeric(df["open"])
    df["high"] = pd.to_numeric(df["high"])
    df["low"] = pd.to_numeric(df["low"])
    df["close"] = pd.to_numeric(df["close"])
    df["volume"] = pd.to_numeric(df["volume"])
    df = df.sort_values("start").reset_index(drop=True)
    return df

# ==== Interface Streamlit ====

st.set_page_config(page_title="Detecção de Tendência", layout="wide")
st.title("📈 Análise de Tendência Recente - Backpack API")

tolerancia = st.slider("Tolerância para lateralidade (%)", min_value=0.0, max_value=2.0, value=0.15)

# ==== Lista de Tickers ====
st.sidebar.header("Configurações de Consulta")

try:
    tickers_url = "https://api.backpack.exchange/api/v1/tickers"
    response = requests.get(tickers_url)
    response.raise_for_status()
    tickers_data = response.json()
    symbol_list = sorted([ticker["symbol"] for ticker in tickers_data])
except Exception as e:
    st.error(f"Erro ao carregar lista de tickers: {e}")
    symbol_list = ["WLD_USDC"]

symbol = st.sidebar.selectbox("Escolha o par de ativos (ticker):", symbol_list, index=symbol_list.index("WLD_USDC") if "WLD_USDC" in symbol_list else 0)

with st.spinner("Carregando dados..."):
    df = obter_dados(symbol)

window_ma = 1
dist_min = 2

n_lp = obter_ultimo_pivot(df, window=window_ma, distancia_minima=dist_min) 
if n_lp > len(df):
    n_lp = len(df)

st.write(f"Número de candles desde o último pivot encontrado (com ajuste): {n_lp}")

# Detecta tendências
tendencia_simples = detectar_tendencia_simples(df, n=n_lp)
tendencia_regressao = detectar_tendencia_regressao(df, n=n_lp, tolerancia=tolerancia)

st.markdown(f"**Tendência Simples (últimos {n_lp} candles)**: `{tendencia_simples}`")
st.markdown(f"**Tendência por Regressão (últimos {n_lp} candles)**: `{tendencia_regressao}`")


# detecta stop loss
entrada = df['close'].iloc[-1]


if tendencia_regressao == "falling":
    resultado = calcular_trade_levels(df, preco_entrada=entrada, tipo='BUY', p=0.2, risk_reward_ratio=2)
elif tendencia_regressao == "rising":
    resultado = calcular_trade_levels(df, preco_entrada=entrada, tipo='SELL', p=0.2, risk_reward_ratio=2)
else:
    resultado = 0

if resultado:
    st.markdown(f"📍 Entrada: {resultado['preco_entrada']}")
    st.markdown(f"⛔ Stop Loss: {resultado['stop_loss']} ({resultado['stop_loss_pct']:.2f}%)")
    st.markdown(f"✅ Take Profit: {resultado['take_profit']} ({resultado['take_profit_pct']:.2f}%)")
    st.markdown(f"🔁 Risk/Reward: {resultado['risk_reward_ratio']}x")
    st.markdown(f"📌 Pivot usado (índice): {len(df) - resultado['pivot2_index']}")
    st.markdown(f"📌 1º Pivot (índice): {len(df) - resultado['pivot1_index']}")
    n = len(df) - resultado['pivot2_index'] + 2
else:
    print("❌ Nenhum pivot válido encontrado.")
    n = n_lp

df_lp = df.tail(n_lp)
df_n = df.tail(n)
print(len(df))
# Calcula médias móveis suavizadas (com centro) para o gráfico
high_smooth = df['high'].rolling(window=window_ma, center=True).mean()
low_smooth = df['low'].rolling(window=window_ma, center=True).mean()

# Regressão linear
x_vals = list(range(len(df_lp)))
y_vals = df_lp["close"].values
a = (n_lp * sum(x_vals[i] * y_vals[i] for i in range(n_lp)) - sum(x_vals) * sum(y_vals)) / \
    (n_lp * sum(x_vals[i]**2 for i in range(n_lp)) - sum(x_vals)**2)
b = (sum(y_vals) - a * sum(x_vals)) / n_lp
y_reg = [a * x + b for x in x_vals]

variacao_pct_reg = (y_reg[-1] - y_reg[0]) / y_reg[0] * 100
st.markdown(f"**Variação da Regressão Linear**: `{variacao_pct_reg:.2f}%`")

y_high = df_n["high"].values
print(y_high,"   ",y_vals)
# Plotagem
fig = go.Figure()
fig.add_trace(go.Candlestick(
    x=df_n["start"],
    open=df_n["open"],
    high=df_n["high"],
    low=df_n["low"],
    close=df_n["close"],
    increasing_line_color="green",
    decreasing_line_color="red",
    name="Candles"
))
start_idx = len(df) - n_lp
end_index = len(df)
fig.add_trace(go.Scatter(
    x=df['start'].iloc[start_idx:end_index + 1],
    y=y_reg,
    mode='lines',
    line=dict(color='blue', dash='dash'),
    name="Regressão Linear"
))

# Ajusta média móvel para o período plotado (cuidado com NaNs da média móvel centralizada)
start_idx = len(df)-n
ma_high_n = high_smooth.iloc[start_idx:].reset_index(drop=True)
ma_low_n = low_smooth.iloc[start_idx:].reset_index(drop=True)

fig.add_trace(go.Scatter(
    x=df_n["start"],
    y=ma_high_n,
    mode='lines',
    line=dict(color='orange'),
    name=f'Média Móvel High ({window_ma})'
))

fig.add_trace(go.Scatter(
    x=df_n["start"],
    y=ma_low_n,
    mode='lines',
    line=dict(color='purple'),
    name=f'Média Móvel Low ({window_ma})'
))

fig.update_layout(
    title=f"Últimos {n} Candles de {symbol} com Regressão Linear e Médias Móveis",
    xaxis_rangeslider_visible=False,
    height=500
)

if resultado:
    # Linha de Stop Loss (vermelha tracejada)
    fig.add_trace(go.Scatter(
        x=df_n["start"],
        y=[resultado["stop_loss"]] * len(df_n),
        mode='lines',
        line=dict(color='red', dash='dash'),
        name='Stop Loss'
    ))

    # Linha de Take Profit (verde tracejada)
    fig.add_trace(go.Scatter(
        x=df_n["start"],
        y=[resultado["take_profit"]] * len(df_n),
        mode='lines',
        line=dict(color='green', dash='dash'),
        name='Take Profit'
    ))

st.plotly_chart(fig, use_container_width=True)
