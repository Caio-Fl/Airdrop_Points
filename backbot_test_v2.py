import streamlit as st
import requests
import time
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from scipy.signal import find_peaks
import os

# --- NOVAS FUNÇÕES DE LÓGICA (ESTILO JS) ---

def calcular_inclinacao_ema(df, coluna_ema, window=3):
    if len(df) < window: return "neutral"
    ema_atual = df[coluna_ema].iloc[-1]
    ema_anterior = df[coluna_ema].iloc[-window]
    diff_pct = (ema_atual - ema_anterior) / ema_anterior * 100
    if diff_pct > 0.01: return "rising"
    elif diff_pct < -0.01: return "falling"
    return "flat"

def contar_toques_ema(df, coluna_ema, tolerancia_pct, lookback=10):
    recent = df.tail(lookback).copy()
    tolerancia = tolerancia_pct / 100
    upper = recent[coluna_ema] * (1 + tolerancia)
    lower = recent[coluna_ema] * (1 - tolerancia)
    toques = ((recent['high'] >= lower) & (recent['low'] <= upper)).sum()
    return toques

# --- FUNÇÕES DE CÁLCULO ORIGINAIS REFORMULADAS PARA EVITAR ERROS ---

def detectar_pivots(df, window=2, distancia_minima=3):
    if len(df) < window * 2: return [], [], np.array([]), np.array([])
    high_smooth = df['high'].rolling(window=window, center=True).mean().fillna(method='bfill').fillna(method='ffill')
    low_smooth = df['low'].rolling(window=window, center=True).mean().fillna(method='bfill').fillna(method='ffill')
    peaks, _ = find_peaks(high_smooth, distance=distancia_minima)
    valleys, _ = find_peaks(-low_smooth, distance=distancia_minima)
    offset = (window - 1) // 2
    return (peaks + offset).tolist(), (valleys + offset).tolist(), peaks + offset, valleys + offset

def detectar_tendencia_regressao(df, n=3, tolerancia=0.1):
    if len(df) < n: return "lateral"
    mids = ((df['high'] + df['low']) / 2).iloc[-n:]
    variacao_pct = (mids.iloc[-1] - mids.iloc[0]) / mids.iloc[0] * 100
    if variacao_pct > tolerancia: return "rising"
    elif variacao_pct < -tolerancia: return "falling"
    return "lateral"

# --- CONFIGURAÇÃO STREAMLIT ---

st.set_page_config(page_title="EMA Bot Backpack", layout="wide")
st.title("📊 EMA Strategy Bot - Optimized")

with st.sidebar:
    evaluate_all_markets = st.checkbox("Verify All Markets", value=True)
    interval = st.selectbox("Interval:", ["5m", "15m", "1h", "4h"], index=1)
    period_hours = st.slider("Period (hours):", 24, 900, 360)
    price_type = st.selectbox("Price Type:", ["LastPrice", "IndexPrice", "MarkPrice"], index=0)
    tolerancia_pct = st.number_input("Entry Tolerance (%)", value=0.20)
    ratio = st.number_input("Risk Reward Ratio", value=2.0)
    max_touches = st.slider("Max Touches (Exhaustion)", 1, 10, 3)
    start_bot = st.button("🚀 Start Bot")
    stop_bot = st.button("🛑 Stop Bot")

if "running" not in st.session_state: st.session_state.running = False

# --- LOOP DE EXECUÇÃO ---

if start_bot: st.session_state.running = True
if stop_bot: st.session_state.running = False

if st.session_state.running:
    # Busca Tickers iniciais
    tickers = requests.get("https://api.backpack.exchange/api/v1/tickers").json()
    sym_list = sorted([t["symbol"] for t in tickers]) if evaluate_all_markets else ["SOL_USDC"]
    
    placeholder_log = st.empty()
    all_signals = []

    for symbol in sym_list:
        try:
            now = int(time.time())
            start_time = now - (period_hours * 3600)
            
            url = "https://api.backpack.exchange/api/v1/klines"
            params = {
                "symbol": symbol,
                "interval": interval,
                "startTime": start_time,
                "endTime": now,
                "klinePriceType": price_type
            }

            response = requests.get(url, params=params)
            
            # TRATAMENTO DE ERRO DA API (Respeitando o original)
            if response.status_code != 200:
                continue
                
            klines = response.json()
            if not klines or len(klines) < 50:
                continue

            df = pd.DataFrame(klines)
            for col in ["open", "high", "low", "close", "volume"]:
                df[col] = df[col].astype(float)
            df["start"] = pd.to_datetime(df["start"])

            # Cálculos de Médias
            for p in [21, 50, 100, 200]:
                df[f"EMA_{p}"] = df["close"].ewm(span=p, adjust=False).mean()

            last = df.iloc[-1]
            price = last["close"]
            tendencia_recente = detectar_tendencia_regressao(df, n=5)

            # --- LÓGICA DE DECISÃO REFINADA (PYTHON + JS) ---
            sinal = None
            motivo = ""

            for p in [21, 50, 100, 200]:
                col_ema = f"EMA_{p}"
                ema_val = last[col_ema]
                delta = ((price - ema_val) / ema_val) * 100
                
                # Novas métricas de validação
                inclinacao = calcular_inclinacao_ema(df, col_ema)
                toques = contar_toques_ema(df, col_ema, tolerancia_pct)

                if abs(delta) < tolerancia_pct:
                    if toques > max_touches: continue # Ignora se houver muitos toques (JS Logic)
                    
                    # BUY: Preço corrigindo (caindo) mas média subindo forte
                    if tendencia_recente == "falling" and inclinacao == "rising":
                        sinal = f"📈 BUY ({col_ema})"
                        motivo = col_ema
                        break
                    # SELL: Preço corrigindo (subindo) mas média caindo forte
                    elif tendencia_recente == "rising" and inclinacao == "falling":
                        sinal = f"📉 SELL ({col_ema})"
                        motivo = col_ema
                        break

            if sinal:
                # Se detectou sinal, adiciona na lista para mostrar no final
                all_signals.append({
                    "Symbol": symbol,
                    "Price": f"{price:.4f}",
                    "Signal": sinal,
                    "EMA Direction": inclinacao,
                    "Recent Touches": toques
                })

        except Exception as e:
            placeholder_log.error(f"Error analyzing {symbol}: {e}")
            continue

    if all_signals:
        st.success(f"Detected {len(all_signals)} opportunities!")
        st.table(pd.DataFrame(all_signals))
    else:
        st.info("Scanning... No high-probability setups found at this moment.")
    
    time.sleep(2) # Pequena pausa entre varreduras
    st.rerun()