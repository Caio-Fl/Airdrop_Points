import streamlit as st
import requests
import time
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from scipy.signal import find_peaks
import os

def intervalo_para_minutos(intervalo):
    if intervalo.endswith("m"):
        return int(intervalo.replace("m", ""))
    elif intervalo.endswith("h"):
        return int(intervalo.replace("h", "")) 
    elif intervalo.endswith("d"):
        return int(intervalo.replace("d", "")) * 24
    else:
        return None

def soma_volume_ultimas_24h(df, col_data='start', col_volume='volume'):
    """
    Calcula o somatório do volume nas últimas 24 horas.
    
    df : DataFrame com dados
    col_data : nome da coluna de timestamp (precisa estar em datetime)
    col_volume : nome da coluna de volume (precisa ser numérico)
    
    Retorna: float (soma do volume)
    """
    df = df.copy()
    df[col_data] = pd.to_datetime(df[col_data])

    agora = pd.Timestamp.now()
    limite = agora - pd.Timedelta(hours=24)

    df_24h = df[df[col_data] >= limite]

    return df_24h[col_volume].sum()

def detectar_tendencia_simples(df, n=3):
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

def detectar_tendencia_regressao(df, n=3, tolerancia=0.1):
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

    offset = (window - 1) // 2

    indices_pivots_alta = peaks + offset
    indices_pivots_baixa = valleys + offset

    return indices_pivots_alta.tolist(), indices_pivots_baixa.tolist(), indices_pivots_alta, indices_pivots_baixa
    
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
    pivots_alta, pivots_baixa,_,_ = detectar_pivots(df, window=2, distancia_minima=3)

    if tipo == 'SELL':
        pivots_validos = [i for i in pivots_alta if df.loc[i, 'high'] > preco_entrada]
        pivots_contrario = [i for i in pivots_baixa if df.loc[i, 'low'] < preco_entrada]
        if not pivots_validos:
            return None
        if not pivots_contrario:
            return None
        pivot1_idx = pivots_contrario[-1]
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
        pivot2_idx = pivots_validos[-1]
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

def calculate_stop_take(df, operation, entry_price, lookback=2,
                        max_stop_loss_pct=0.03, max_take_profit_pct=0.05, buffer_pct=0.002):
    """
    Calcula stop loss e take profit com base no último pivô relevante antes da entrada,
    respeitando limites máximos e mínimos de variação percentual.

    df: dataframe com colunas ['high', 'low', 'close']
    operation: "BUY" ou "SELL"
    entry_price: preço de entrada
    lookback: quantos candles antes/depois para identificar pivôs
    max_stop_loss_pct: limite máximo de stop loss (ex: 0.03 = 3%)
    max_take_profit_pct: limite máximo de take profit (ex: 0.05 = 5%)
    buffer_pct: margem de segurança sobre o pivô (ex: 0.002 = 0.2%)
    """
    df = df.copy()

    # Limites mínimos
    min_stop_loss_pct = 0.005   # 0.5%
    min_take_profit_pct = 0.01  # 1%

    # Calcular pivôs
    df['pivot_high'] = df['high'][
        (df['high'].shift(lookback) < df['high']) &
        (df['high'].shift(-lookback) < df['high'])
    ]

    df['pivot_low'] = df['low'][
        (df['low'].shift(lookback) > df['low']) &
        (df['low'].shift(-lookback) > df['low'])
    ]
    
    # Pegar o índice do candle mais recente
    last_idx = df.index[-1]

    stop_loss = None
    take_profit = None

    if operation.upper() == "SELL":
        # Último topo relevante
        last_pivot_high = df.loc[:last_idx - 1]['pivot_high'].dropna()
        if not last_pivot_high.empty:
            raw_stop = last_pivot_high.iloc[-1] * (1 + buffer_pct)
            max_stop = entry_price * (1 + max_stop_loss_pct)
            stop_loss = min(raw_stop, max_stop)
            min_stop = entry_price * (1 + min_stop_loss_pct)
            stop_loss = max(stop_loss, min_stop)
        else:
            stop_loss = entry_price * (1 + min_stop_loss_pct)

        # Último fundo relevante
        last_pivot_low = df.loc[:last_idx - 1]['pivot_low'].dropna()
        if not last_pivot_low.empty:
            raw_take = last_pivot_low.iloc[-1] * (1 + buffer_pct)
            max_take = entry_price * (1 - max_take_profit_pct)
            take_profit = max(raw_take, max_take)
            min_take = entry_price * (1 - min_take_profit_pct)
            take_profit = min(take_profit, min_take)
        else:
            take_profit = entry_price * (1 - min_take_profit_pct)

    elif operation.upper() == "BUY":
        # Último fundo relevante
        last_pivot_low = df.loc[:last_idx - 1]['pivot_low'].dropna()
        if not last_pivot_low.empty:
            raw_stop = last_pivot_low.iloc[-1] * (1 - buffer_pct)
            max_stop = entry_price * (1 - max_stop_loss_pct)
            stop_loss = max(raw_stop, max_stop)
            min_stop = entry_price * (1 - min_stop_loss_pct)
            stop_loss = min(stop_loss, min_stop)
        else:
            stop_loss = entry_price * (1 - min_stop_loss_pct)

        # Último topo relevante
        last_pivot_high = df.loc[:last_idx - 1]['pivot_high'].dropna()
        if not last_pivot_high.empty:
            raw_take = last_pivot_high.iloc[-1] * (1 - buffer_pct)
            max_take = entry_price * (1 + max_take_profit_pct)
            take_profit = min(raw_take, max_take)
            min_take = entry_price * (1 + min_take_profit_pct)
            take_profit = max(take_profit, min_take)
        else:
            take_profit = entry_price * (1 + min_take_profit_pct)

    else:
        raise ValueError("operation deve ser 'BUY' ou 'SELL'")

    # Calcular diferenças percentuais
    diff_stop_pct = abs((entry_price - stop_loss) / entry_price) * 100
    diff_take_pct = abs((take_profit - entry_price) / entry_price) * 100

    # Relação risco/retorno
    risk_reward_ratio = round(diff_take_pct / diff_stop_pct, 2) if diff_stop_pct != 0 else None

    return {
        "stop_loss": round(stop_loss, 5),
        "take_profit": round(take_profit, 5),
        "diff_stop_pct": round(diff_stop_pct, 2),
        "diff_take_pct": round(diff_take_pct, 2),
        "risk_reward_ratio": risk_reward_ratio
    }

def analisar_pullback_volume(df, pivot_index, tendencia, n=3, media_volume_window=10, limite_proporcao_contraria=0.70):
    """
    Analisa o volume dos candles desde o último pivot até agora, levando em conta a tendência (alta ou baixa).

    Parâmetros:
        df: DataFrame com ['open', 'close', 'volume']
        pivot_index: índice do último pivot detectado
        tendencia: str, 'rising' ou 'falling'
        n: número de candles desde o pivot (None para pegar todos até o fim)
        media_volume_window: janela para cálculo de volume médio de referência
        limite_proporcao_contraria: limite de volume de candles contrários à tendência

    Retorna:
        dict com métricas e classificação
    """

    if n is not None:
        candles = df.iloc[pivot_index+1 : pivot_index+1+n]
    else:
        candles = df.iloc[pivot_index+1:]

    if candles.empty:
        return {"Error": "No candles after pivot."}

    volume_total = candles["volume"].sum()
    volume_medio_ref = df["volume"].iloc[-media_volume_window:].mean()

    
    # 👉 Se a tendência for lateral, usamos outro critério
    if tendencia == 'lateral':
        desvio_volume = candles["volume"].std()
        media_volume = candles["volume"].mean()

        if media_volume < volume_medio_ref * 0.75 and desvio_volume < volume_medio_ref * 0.25:
            classificacao = "Consolidation (Low and Stable Volume)"
        elif media_volume > volume_medio_ref * 1.25:
            classificacao = "Possible breakout (above average volume in laterality)"
        else:
            classificacao = "Neutral Moviment in Laterality"

        return {
            "volume_total": volume_total,
            "volume_medio_ref": volume_medio_ref,
            "media_volume": media_volume,
            "desvio_volume": desvio_volume,
            "classificacao": classificacao
        }

    # Classificação dos candles:
    if tendencia == 'rising':
        volume_contrario = candles[candles["close"] < candles["open"]]["volume"].sum()
        volume_a_favor = candles[candles["close"] > candles["open"]]["volume"].sum()
    elif tendencia == 'falling':
        volume_contrario = candles[candles["close"] > candles["open"]]["volume"].sum()
        volume_a_favor = candles[candles["close"] < candles["open"]]["volume"].sum()
    else:
         raise ValueError("Trend need to be 'rising', 'falling' ou 'lateral'!")

    proporcao_contraria = volume_contrario / volume_total if volume_total > 0 else 0

    # Classificação do pullback
    if volume_total < volume_medio_ref * 0.75:
        if proporcao_contraria > limite_proporcao_contraria:
            classificacao = "dangerous pullback (week volume, but dominant counter candles)"
        else:
            classificacao = "helph pullback (week volume, trend should continue)"
    elif proporcao_contraria > limite_proporcao_contraria:
        classificacao = "possible reversal (dominant counter volume)"
    else:
        classificacao = "neutral pullback (volume within normal)"

    return {
        "volume_total": volume_total,
        "volume_medio_ref": volume_medio_ref,
        "volume_a_favor": volume_a_favor,
        "volume_contrario": volume_contrario,
        "proporcao_contraria": proporcao_contraria,
        "classificacao": classificacao
    }

def identificar_congestao(df: pd.DataFrame, timeframe: str) -> bool:
    # Cálculo das EMAs
    df['ema21'] = df['close'].ewm(span=21).mean()
    df['ema50'] = df['close'].ewm(span=50).mean()
    df['ema100'] = df['close'].ewm(span=100).mean()
    df['ema200'] = df['close'].ewm(span=200).mean()

    # Parâmetros por timeframe
    limites_por_tf = {
        "5m": {"dist_pct_max": 0.5, "inclinacao_max": 0.1, "atraso": 8},
        "15m": {"dist_pct_max": 1, "inclinacao_max": 0.15, "atraso": 5},
        "1h": {"dist_pct_max": 1.5, "inclinacao_max": 0.25, "atraso": 3},
        "4h": {"dist_pct_max": 2, "inclinacao_max": 0.35, "atraso": 3},
        "1d": {"dist_pct_max": 2.5, "inclinacao_max": 0.4, "atraso": 2}
    }

    # Parâmetros default se timeframe não for reconhecido
    params = limites_por_tf.get(timeframe, {"dist_pct_max": 2.5, "inclinacao_max": 0.1, "atraso": 5})
    atraso = params["atraso"]

    # Últimos valores das EMAs
    emas = df[['ema21', 'ema50', 'ema100', 'ema200']].iloc[-1]
    max_ema = emas.max()
    min_ema = emas.min()

    # Verifica proximidade entre EMAs
    dist_pct = abs(max_ema - min_ema) / max_ema * 100
    todas_proximas = dist_pct < params["dist_pct_max"]
    
    # Verifica horizontalidade (baixa inclinação)
    inclinacoes = {}
    inclinacoes_long = {}
    direcoes_ema = {}
    for period in [21, 50, 100, 200]:
        atual = df[f'ema{period}'].iloc[-1]
        anterior = df[f'ema{period}'].iloc[-1 - atraso]
        anterior_long = df[f'ema{period}'].iloc[-1 - (10*atraso)]
        inclinacao_pct = (atual - anterior) / anterior * 100
        inclinacao_pct_long = (atual - anterior_long) / anterior_long * 100
        inclinacoes[period] = abs(inclinacao_pct)
        # Verificar se a inclinação é positiva ou negativa
        if inclinacao_pct_long > 0.025:
            direcoes_ema[period] = "rising"
        elif inclinacao_pct_long < -0.025:
            direcoes_ema[period] = "falling"
        else:
            direcoes_ema[period] = "flat"

    # Pelo menos 3 inclinações devem estar abaixo do limite
    todas_horizontais = sum(i < params["inclinacao_max"] for i in inclinacoes.values()) >= 3

    print(params["dist_pct_max"], todas_proximas, params["inclinacao_max"], todas_horizontais,inclinacoes[21],inclinacoes[50],inclinacoes[100],inclinacoes[200])
    return todas_proximas and todas_horizontais, direcoes_ema

# Página Streamlit
st.set_page_config(
    page_title="EMA Trade Bot Backpack Exchange",
    page_icon=":chart_with_upwards_trend:",
    layout="wide"
)
 
# CSS para aumentar comprimento
st.markdown("""
    <style>
        html, body, [data-testid="stApp"] {
            min-height: 900px;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown(
    """
    <h1 style='text-align: center; color: white;'>
        📊 EMA Strategy Trade Bot - Backpack Exchange
    </h1>
    """,
    unsafe_allow_html=True
)

# 📞 Configuração do WhatsApp CallMeBot
NUMERO = "5521979782518"
APIKEY = "4751080"

all_signals = []

# URL da API
url = "https://api.backpack.exchange/api/v1/tickers"

# Requisição GET
response = requests.get(url)
response.raise_for_status()  # dispara erro se a requisição falhar

# Converte para JSON
tickers = response.json()

# Extrai a lista de symbols
symbol = sorted([ticker["symbol"] for ticker in tickers])

col1, col2, col3, col4 = st.columns([0.15, 0.5, 2,0.15]) # layout da página em colunas
with col2:
        

        # Mostra no selectbox
        evaluate_all_markets = st.checkbox("Verify All Markets", value=True)
        if evaluate_all_markets == False:
            sym = [st.selectbox("Choose Market:", symbol)]
        else:
            sym = symbol

        start = st.button("🚀 Start Bot")
        stop = st.button("🛑 Stop Bot")
        
        # 🎛 Configurações do usuário
        
        interval = st.selectbox("Interval:", ["5m", "15m", "1h", "4h"], index=1)

        period_hours = st.slider("Period (hours):", 48, 900, 360)
        price_type = st.selectbox("Price Type:", ["LastPrice", "IndexPrice", "MarkPrice"], index=0)
        tolerancia_pct = st.number_input("Entry Tolerancy (%)", value=0.25)
        calcular_stop = st.checkbox("Auto Calculate Stop Loss and Take Profit", value=True)
        if calcular_stop:
            ratio = st.number_input("Risk Reward Ratio", value=2)
            stop_loss_pct = 1
            take_profit_pct = 2
        else:
            take_profit_pct = st.number_input("Take Profit (%)", value=2)
            stop_loss_pct = st.number_input("Stop Loss (%)", value=1)
        refresh_interval = 0.1#st.slider("⏱ Update (seconds):", 1, 300, 1)
        pasta_graficos = st.text_input("Folder to save graphics:", value="C:\\Users\\0335372\\Desktop\\grafico_bot\\")
        enviar_whatsapp = st.checkbox("Send Signals to the registred WhatsApp", value=True)

        # Cria pasta se não existir
        if not os.path.exists(pasta_graficos):
            os.makedirs(pasta_graficos)

        # EMAs por timeframe
        ema_periods = {
            "5m": [21, 50, 100, 200],
            "15m": [21, 50, 100, 200],
            "1h": [21, 50, 100, 200],
            "4h": [21, 50, 100, 200],
            "1d": [21, 50, 100, 200]
        }

        # Inicializa variáveis de estado
        if "running" not in st.session_state:
            st.session_state.running = False
        if "last_run" not in st.session_state:
            st.session_state.last_run = 0
        if "csv_logs" not in st.session_state:
            st.session_state.csv_logs = []

with col3:
    
    if "placeholder_chart" not in st.session_state:
        st.session_state.placeholder_chart = st.empty()
    if "placeholder_log" not in st.session_state:
        st.session_state.placeholder_log = st.empty()

    if start:
        st.session_state.running = True
    if stop:
        st.session_state.running = False
    if st.session_state.running:
        for symbol in sym:     
            # 🔄 Execução do bot
            now = int(time.time())
            if (st.session_state.running and (now - st.session_state.last_run >= refresh_interval)):
                st.session_state.last_run = now

                try:
                    print(f"\n{symbol}")
                    # Consulta dados da API
                    start_time = now - period_hours * 3600
                    url = "https://api.backpack.exchange/api/v1/klines"
                    params = {
                        "symbol": symbol,
                        "interval": interval,
                        "startTime": start_time,
                        "endTime": now,
                        "klinePriceType": price_type
                    }

                    response = requests.get(url, params=params)
                    response.raise_for_status()
                    klines = response.json()
                    if klines:
                        df = pd.DataFrame(klines)
                        for col in ["open", "high", "low", "close", "volume", "quoteVolume"]:
                            if col in df.columns:
                                df[col] = df[col].astype(float)
                        df["start"] = pd.to_datetime(df["start"])

                        # Calcular EMAs
                        for period in ema_periods[interval]:
                            df[f"EMA_{period}"] = df["close"].ewm(span=period, adjust=False).mean()

                        df['is_bull'] = df['close'] > df['open']

                        # 📊 Bollinger Bands (period=20, k=2)
                        bb_period = 20
                        bb_std = 2

                        df['BB_Middle'] = df['close'].rolling(window=bb_period).mean()
                        df['BB_Std'] = df['close'].rolling(window=bb_period).std()
                        df['BB_Upper'] = df['BB_Middle'] + bb_std * df['BB_Std']
                        df['BB_Lower'] = df['BB_Middle'] - bb_std * df['BB_Std']

                        # Verifica se nos últimos 5 candles o preço atingiu ou passou as EMAs
                        last5 = df.tail(10)
                        tolerancia = 0.01 * tolerancia_pct / 100

                        # EMA_21
                        ema21_upper = last5['EMA_21'] * (1 + tolerancia)
                        ema21_lower = last5['EMA_21'] * (1 - tolerancia)
                        touched_ema21 = (
                            ((last5['high'] >= ema21_lower) & (last5['low'] <= ema21_upper))
                        ).any()

                        # EMA_50
                        ema50_upper = last5['EMA_50'] * (1 + tolerancia)
                        ema50_lower = last5['EMA_50'] * (1 - tolerancia)
                        touched_ema50 = (
                            ((last5['high'] >= ema50_lower) & (last5['low'] <= ema50_upper))
                        ).any()

                        # EMA_100
                        ema100_upper = last5['EMA_100'] * (1 + tolerancia)
                        ema100_lower = last5['EMA_100'] * (1 - tolerancia)
                        touched_ema100 = (
                            ((last5['high'] >= ema100_lower) & (last5['low'] <= ema100_upper))
                        ).any()

                        # EMA_200
                        ema200_upper = last5['EMA_200'] * (1 + tolerancia)
                        ema200_lower = last5['EMA_200'] * (1 - tolerancia)
                        touched_ema200 = (
                            ((last5['high'] >= ema200_lower) & (last5['low'] <= ema200_upper))
                        ).any()

                        # Separar candles de compra e venda
                        bull_volumes = df[df['is_bull']]['volume']
                        bear_volumes = df[~df['is_bull']]['volume']

                        # Pegar últimos 30
                        last30_bull_volumes = bull_volumes.tail(30)
                        last30_bear_volumes = bear_volumes.tail(30)

                        # Volume médio para candles de compra e venda
                        bull_avg = bull_volumes.mean()
                        bear_avg = bear_volumes.mean()

                        print(f"Mean Buy Volume of Time Window: {bull_avg:.2f}")
                        print(f"Mean Sell Volume of Time Window: {bear_avg:.2f}")

                        # último preço
                        
                        last = df.iloc[-1]
                        price = last["close"]

                        # Detectar número de candles de retorno a média a partir do último pivot
                        n = obter_ultimo_pivot(df, window=2, distancia_minima=3) 
                        if n > len(df):
                            n = len(df)

                        # Últimos n candles
                        ultimos_n = df.iloc[-n:]

                        # Maior volume entre os últimos n candles
                        vol_last = ultimos_n['volume'].max()
                        vol_medio = df["volume"].mean()
                        

                        # Tendência de retorno
                        tendencia_simples = detectar_tendencia_simples(df, n)

                        tendencia_regressao = detectar_tendencia_regressao(df, n, tolerancia=0.3)

                        tendencia_recente = tendencia_regressao
                        
                        print(f"Recent Trend to Last {n} Candles: {tendencia_simples}")
                        print(f"Recent Trend by Regression to Last {n} Candles: {tendencia_regressao}")
                        
                        pullback_volume = analisar_pullback_volume(df, pivot_index=n, tendencia=tendencia_recente, n=n, media_volume_window=n*5, limite_proporcao_contraria=0.70)
                        
                        congestao, direcoes_ema = identificar_congestao(df, timeframe=interval)
                        
                        ema21 = last.get("EMA_21")
                        ema50 = last.get("EMA_50")
                        ema100 = last.get("EMA_100")
                        ema200 = last.get("EMA_200")
                        sinal = "⚪ No Signal Detected"
                        preco_entrada = stop_loss = take_profit = None
                        motivo = ""
                        
                        if ema21 and ema50 and ema100 and ema200:
                            delta21 = ((price - ema21) / ema21) * 100
                            delta50 = ((price - ema50) / ema50) * 100
                            delta100 = ((price - ema100) / ema100) * 100
                            delta200 = ((price - ema200) / ema200) * 100
                            
                            # ---- EMA_21 ----
                            if (-tolerancia_pct < delta21 < tolerancia_pct):
                                if tendencia_recente == "rising" and congestao == False and pullback_volume["classificacao"] != "possible reversal (dominant counter volume)" and pullback_volume["classificacao"] != "dangerous pullback (week volume, but dominant counter candles)":
                                    sinal = f"📉 SELL (resistance EMA_21): price {price:.5f} touched EMA_21 coming from below and the weak volume indicates this as pullback."
                                    motivo = "EMA_21"
                                elif tendencia_recente == "falling" and congestao == False and pullback_volume["classificacao"] != "possible reversal (dominant counter volume)" and pullback_volume["classificacao"] != "dangerous pullback (week volume, but dominant counter candles)":
                                    sinal = f"📈 BUY (support EMA_21): price {price:.5f} touched EMA_21 coming from above and the weak volume indicates this as pullback."
                                    motivo = "EMA_21"

                            # ---- EMA_50 ----
                            elif (-tolerancia_pct < delta50 < tolerancia_pct):
                                if tendencia_recente == "rising" and congestao == False and pullback_volume["classificacao"] != "possible reversal (dominant counter volume)" and pullback_volume["classificacao"] != "dangerous pullback (week volume, but dominant counter candles)":
                                    sinal = f"📉 SELL (resistance EMA_50): price {price:.5f} touched EMA_50 coming from below and the weak volume indicates this as pullback."
                                    motivo = "EMA_50"
                                elif tendencia_recente == "falling" and congestao == False and pullback_volume["classificacao"] != "possible reversal (dominant counter volume)" and pullback_volume["classificacao"] != "dangerous pullback (week volume, but dominant counter candles)":
                                    sinal = f"📈 BUY (support EMA_50): price {price:.5f} touched EMA_50 coming from above and the weak volume indicates this as pullback."
                                    motivo = "EMA_50"

                            # ---- EMA_100 ----
                            elif (-tolerancia_pct < delta100 < tolerancia_pct):
                                if tendencia_recente == "rising" and congestao == False and pullback_volume["classificacao"] != "possible reversal (dominant counter volume)" and pullback_volume["classificacao"] != "dangerous pullback (week volume, but dominant counter candles)":
                                    sinal = f"📉 STRONG SELL (resistance EMA_100): price {price:.5f} touched EMA_100 coming from below and the weak volume indicates this as pullback."
                                    motivo = "EMA_100"
                                elif tendencia_recente == "falling" and congestao == False and pullback_volume["classificacao"] != "possible reversal (dominant counter volume)" and pullback_volume["classificacao"] != "dangerous pullback (week volume, but dominant counter candles)":
                                    sinal = f"📈 STRONG BUY (support EMA_100): price {price:.5f} touched EMA_100 coming from above and the weak volume indicates this as pullback."
                                    motivo = "EMA_100"

                            # ---- EMA_200 ----
                            elif (-tolerancia_pct < delta200 < tolerancia_pct):
                                if tendencia_recente == "rising" and congestao == False and pullback_volume["classificacao"] != "possible reversal (dominant counter volume)" and pullback_volume["classificacao"] != "dangerous pullback (week volume, but dominant counter candles)":
                                    sinal = f"📉 VERY STRONG SELL (resistance EMA_200): price {price:.5f} touched EMA_200 coming from below and the weak volume indicates this as pullback."
                                    motivo = "EMA_200"
                                elif tendencia_recente == "falling" and congestao == False and pullback_volume["classificacao"] != "possible reversal (dominant counter volume)" and pullback_volume["classificacao"] != "dangerous pullback (week volume, but dominant counter candles)":
                                    sinal = f"📈 VERY STRONG BUY (support EMA_200): price {price:.5f} touched EMA_200 coming from above and the weak volume indicates this as pullback."
                                    motivo = "EMA_200"

                            if "BUY" in sinal:
                                preco_entrada = price * (1)
                                if calcular_stop:
                                    result = calcular_trade_levels(df, preco_entrada, tipo='BUY', p=0.2, risk_reward_ratio=ratio)
                                    stop_loss = result['stop_loss']
                                    take_profit = result['take_profit']
                                    print(result)
                                else:
                                    stop_loss = price * (1 - stop_loss_pct/100)
                                    take_profit = price * (1 + take_profit_pct/100)
                            elif "SELL" in sinal:
                                preco_entrada = price * (1)
                                stop_loss = price * (1 + stop_loss_pct/100)
                                take_profit = price * (1 - take_profit_pct/100)
                                if calcular_stop:
                                    result = calcular_trade_levels(df, preco_entrada, tipo='SELL', p=0.2, risk_reward_ratio=ratio)
                                    stop_loss = result['stop_loss']
                                    take_profit = result['take_profit']
                                    print(result)
                                else:
                                    stop_loss = price * (1 + stop_loss_pct/100)
                                    take_profit = price * (1 - take_profit_pct/100)

                        # Gráfico
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
                        fig.add_trace(go.Scatter(
                            x=df["start"], y=df["BB_Upper"],
                            line=dict(color='rgba(255, 215, 0, 0.3)'),  # amarelo claro
                            name='BB Upper'
                        ))
                        fig.add_trace(go.Scatter(
                            x=df["start"], y=df["BB_Lower"],
                            line=dict(color='rgba(255, 215, 0, 0.3)'),  # amarelo claro
                            name='BB Lower'
                        ))  

                        # Volume Bars    
                        fig.add_trace(go.Bar(
                            x=df["start"], y=df["volume"], name="Volume",
                            marker=dict(color='rgba(150, 150, 150, 0.3)'), yaxis='y2'
                        ))
                        fig.update_layout(
                            title=f"{symbol} - {interval}",
                            template="plotly_dark", height=700,
                            yaxis=dict(title="Price (USD)",domain=[0.25, 1]),
                            yaxis2=dict(title="Volume", domain=[0, 0.20], side='right', showgrid=False)
                        )

                        # Confirma que a pasta existe
                        if not os.path.exists(pasta_graficos):
                            os.makedirs(pasta_graficos)

                        # Monta o nome do arquivo
                        if ("BUY" in sinal) or ("SELL" in sinal):
                            print(f"sinal: {sinal}")
                            fig_filename = f"grafico_{symbol}_{interval}_{int(time.time())}.png"
                            fig_path = os.path.join(pasta_graficos, fig_filename)

                            try:
                                print(f"Saving chart at: {fig_path}")
                                # Salva informando explicitamente o formato
                                fig.write_image(fig_path, format="png")
                                print("✅ Graph saved successfully!")
                            except Exception as e:
                                st.session_state.placeholder_log.warning(f"⚠ Was not possible to save the graph: {e}")

                        # Show graph
                        st.session_state.placeholder_chart.plotly_chart(fig, use_container_width=True, key=symbol)

                        ## Log ##
                        if ema200 > ema100 > ema50 > ema21:
                            tendency = "📉 Strong bearish trend"
                            reason = "All EMAs aligned downward; consider selling only."
                        elif ema21 > ema50 > ema100 > ema200:
                            tendency = "📈 Strong bullish trend"
                            reason = "All EMAs aligned upward; consider buying only."
                        else:
                            # Procura possíveis reversões de curto prazo
                            if ema21 > ema50 and ema50 < ema100:
                                tendency = "⚠️ Possible bullish reversal"
                                reason = "EMA_21 crossed above EMA_50, price may be turning up."
                            elif ema21 < ema50 and ema50 > ema100:
                                tendency = "⚠️ Possible bearish reversal"
                                reason = "EMA_21 crossed below EMA_50, price may be turning down."
                            # Procura possíveis reversões ou cruzamentos de longo prazo
                            elif ema50 > ema100 and ema100 < ema200:
                                tendency = "⚠️ Possible medium-term bullish reversal"
                                reason = "EMA_50 is above EMA_100, and EMA_100 is below EMA_200; market might be starting to reverse up."
                            elif ema50 < ema100 and ema100 > ema200:
                                tendency = "⚠️ Possible medium-term bearish reversal"
                                reason = "EMA_50 is below EMA_100, and EMA_100 is above EMA_200; market might be starting to reverse down."
                            else:
                                tendency = "ℹ️ No clear trend"
                                reason = "EMAs mixed; wait for a clearer signal."
                            
                        log_text = (
                            f"📊 Last Price: {price:.5f}"
                            f"\n➡️ EMA_21: {ema21:.5f} | Δ%: {delta21:.3f}"
                            f"\n➡️ EMA_50: {ema50:.5f} | Δ%: {delta50:.3f}"
                            f"\n➡️ EMA_100: {ema100:.5f} | Δ%: {delta100:.3f}"
                            f"\n➡️ EMA_200: {ema200:.5f} | Δ%: {delta200:.3f}"
                            f"\n📦 Last Candle Volume: {vol_last:.2f} | Average Volume: {vol_medio:.2f}"
                            f"\n📦 Last 30 Buying Candle Volume: {last30_bull_volumes.sum():.2f} | Last 30 Selling Candle Volume: {last30_bear_volumes.sum():.2f}"
                            f"\n{sinal}"
                            f"\nPrice Trend: {tendency}"
                            f"\nNote: {reason}"
                        )       
                        if touched_ema21 or touched_ema50 or touched_ema100 or touched_ema200:
                            touched_list = (f"")
                            not_touched_list = (f"")
                            if touched_ema21:
                                touched_list += (f"EMA_21")
                            else:
                                not_touched_list += (f" EMA_21")
                            if touched_ema50:
                                touched_list += (f" EMA_50")
                            else:
                                not_touched_list += (f" EMA_50")
                            if touched_ema100:
                                touched_list += (f" EMA_100")
                            else:
                                not_touched_list += (f" EMA_100")
                            if touched_ema200:
                                touched_list += (f" EMA_200")
                            else:
                                not_touched_list += (f" EMA_200")

                            # Se quiser, transforma em string separada por vírgula
                            touched_str = (touched_list) if touched_list else ""
                            log_text += (
                                f"\n\n🔍 Verification of Last 10 candles:"
                                f"\n- EMA_21: {'⚠️ Already Touched' if touched_ema21 else '👍 Not Touched'}"
                                f"\n- EMA_50: {'⚠️ Already Touched' if touched_ema50 else '👍 Not Touched'}"
                                f"\n- EMA_100: {'⚠️ Already Touched' if touched_ema100 else '👍 Not Touched'}"
                                f"\n- EMA_200: {'⚠️ Already Touched' if touched_ema200 else '👍 Not Touched'}"
                                f"\nAdvice: Price already touched {touched_str}, so the setup may be late or there is a congestion. \n        Better to wait for a stronger signal near {not_touched_list}."
                                f"\nCongestion: {'Detected'if congestao else 'Not Detected'}"
                                f"\nLong-term (EMA_200) Trend: {direcoes_ema[max(direcoes_ema.keys())]}"
                            )
                        else:
                            touched_str = ""
                            time_window = intervalo_para_minutos(interval) * 10
                            log_text += (
                                f"\n\n🔍 Verifying the Last 10 candles: The price has not touched any of the EMA's in the last {time_window} {interval[-1]}\n"
                            )
                        if preco_entrada:
                            # Hora atual
                            agora = pd.Timestamp.now()

                            # Filtro para últimos 24h
                            ultimo_dia = agora - pd.Timedelta(hours=24)
                            df_ultimas_24h = df[df['start'] >= ultimo_dia]

                            # Somatório do volume nas últimas 24h
                            day_volume = soma_volume_ultimas_24h(df)
                            if day_volume <= 30000:
                                volume_info = "⚠️ 24h Volume is Lower than $30k (risk of large price variation)."
                            else:
                                volume_info = f"24h Volume is helph."
                            info = f"{pullback_volume['classificacao']} + {volume_info}"
                            log_text += (
                                f"\n✅ Entry: {preco_entrada:.4f}"
                                f"\n🛡 Stop Loss: {stop_loss:.4f}"
                                f"\n🎯 Take Profit: {take_profit:.4f}"
                                f"🔁 Risk/Reward: {(take_profit/stop_loss):.2f}x"
                                f"{volume_info}"
                                f"Pullback Info: {info}"
                            )
                            
                            # Advice opcional
                            advice = ""
                            if touched_str != "":
                                advice = (
                                    f"Advice: Price already touched {touched_str}, so the setup may be late or there is a congestion. "
                                    f"May be better to wait for a stronger signal near {not_touched_list}."
                                )

                            all_signals.append({
                                "Symbol": symbol,
                                "Entry Price": preco_entrada,
                                "Stop Loss": stop_loss,
                                "Take Profit": take_profit,
                                "Reason": motivo,
                                "Buy Mean Volume": last30_bull_volumes.sum(),
                                "Sell Mean Volume": last30_bear_volumes.sum(),
                                "Mean Volume": vol_medio,
                                "EMA 21": f"{ema21:.4f} {'⚠️' if touched_ema21 else ''}",
                                "EMA 50": f"{ema50:.4f} {'⚠️' if touched_ema50 else ''}",
                                "EMA 100": f"{ema100:.4f} {'⚠️' if touched_ema100 else ''}",
                                "EMA 200": f"{ema100:.4f} {'⚠️' if touched_ema200 else ''}",
                                "Signal": (
                                    f"<div style='text-align: left; font-size: 11px; line-height: 1.3;'>"
                                    f"<b>{sinal}</b><br>"
                                    f"<b>Price Trend from</b>: {tendency}<br>"
                                    f"<span style='margin-left:12px; display: block;'>↳ Note that {reason}</span>"
                                    f"<span style='margin-left:12px; display: block;'>↳ Pullback Info: {pullback_volume['classificacao']}</span>"
                                    f"<span style='margin-left:12px; display: block;'>↳ {volume_info}</span>"
                                    + (f"<div style='margin-top:4px; color:orange;'>{advice}</div>" if advice else "")
                                    + "</div>"
                                )
                            })
                        
                        st.session_state.placeholder_log.code(log_text)

                        ## Save in CSV and send in WhatsApp if there is signal ##
                        if preco_entrada:
                            st.session_state.csv_logs.append({
                                "timestamp": pd.Timestamp.now(),
                                "symbol": symbol,
                                "interval": interval,
                                "reason": motivo,
                                "signal": sinal,
                                "price": price,
                                "entry": preco_entrada,
                                "stop loss": stop_loss,
                                "take profit": take_profit,
                                "Last Volume": vol_last,
                                "Mean Volume": vol_medio
                            })
                            pd.DataFrame(st.session_state.csv_logs).to_csv("sinais_log.csv", index=False)

                            df['start'] = pd.to_datetime(df['start'])

                            
                            msg_whatsapp = (
                                f"🤖 Signal detected in {symbol}!\n"
                                f"{sinal}\n"
                                f"Entry: {preco_entrada:.2f} | Stop Loss: {stop_loss:.2f} | Take Profit: {take_profit:.2f}\n"
                                f"{volume_info}\n"
                                f"\n\n\n Log of Analysis: \n{log_text}"
                            )
                            if enviar_whatsapp:
                                mensagem = requests.utils.quote(msg_whatsapp)
                                url_whatsapp = f"https://api.callmebot.com/whatsapp.php?phone={NUMERO}&text={mensagem}&apikey={APIKEY}"
                                r = requests.get(url_whatsapp)
                                if r.status_code == 200:
                                    log_text += (f"\n\n📩 Signal sended to WhatsApp!")
                                    st.session_state.placeholder_log.code(log_text)
                                else:
                                    st.session_state.placeholder_log.warning("⚠ Error while sending message to WhatsApp.")

                    else:
                        st.session_state.placeholder_log.warning("No Data Returned by Backpack klines!")

                except Exception as e:
                    st.session_state.placeholder_log.error(f"Error: {e}")
            
            # Pequeno sleep para evitar loops rápidos em testes
            time.sleep(0.4)  

    if (all_signals) and (evaluate_all_markets == True):
        # CSS para compactar as linhas da tabela e ajustar fonte
        st.markdown("""
            <style>
            .dataframe tbody tr th, .dataframe tbody tr td {
                padding: 2px 4px !important;  /* Reduz o espaçamento interno */
                font-size: 11px !important;   /* Diminui a fonte */
            }
            </style>
        """, unsafe_allow_html=True)

        # Exibir dataframe
        df_signals = pd.DataFrame(all_signals)
        df_signals_fmt = df_signals.copy()
        cols_4dec = ["Entry Price", "Stop Loss", "Take Profit"]
        cols_2dec = ["Buy Mean Volume", "Sell Mean Volume", "Mean Volume"]

        for col in cols_4dec:
            df_signals_fmt[col] = df_signals_fmt[col].apply(lambda x: f"{x:.4f}" if isinstance(x, (int, float)) else x)

        for col in cols_2dec:
            df_signals_fmt[col] = df_signals_fmt[col].apply(lambda x: f"{x:.2f}" if isinstance(x, (int, float)) else x)
                

        # Função para gerar HTML compacto
        def gerar_tabela_html_compacta(df):
            html = """
            <style>
                table {
                    border-collapse: collapse;
                    width: 100%;
                    font-size: 11px;
                }
                th, td {
                    border: 1px solid #444;
                    text-align: left;
                    padding: 2px 4px;
                    text-align: center;
                }
                th {
                    background-color: #222;
                    color: #fff;
                }
                tr:nth-child(even) {
                    background-color: #333;
                }
            </style>
            <table>
                <thead>
                    <tr>""" + "".join(f"<th>{col}</th>" for col in df.columns) + "</tr></thead><tbody>"
            for _, row in df.iterrows():
                html += "<tr>" + "".join(f"<td>{row[col]}</td>" for col in df.columns) + "</tr>"
            html += "</tbody></table>"
            return html

        # Exibir tabela
        st.markdown(gerar_tabela_html_compacta(df_signals_fmt), unsafe_allow_html=True)