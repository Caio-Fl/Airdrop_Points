def get_klines_data(exchange, sym, interval, price_type="last", market_id=None):

    import requests
    import pandas as pd
    import time
    from datetime import datetime, timezone 
    import cloudscraper

    now = int(time.time())
    
    # Lógica de períodos original
    if interval == "15m":
        period_hours = 360
    elif interval == "1h":
        period_hours = 720
    elif interval == "4h":
        period_hours = 892
    elif interval == "1d":
        period_hours = 3600
    else:
        period_hours = 120

    start_time = now - period_hours * 3600
    
    try:
        # --- LÓGICA BACKPACK ---
        if exchange.lower() == "backpack":
            url = "https://api.backpack.exchange/api/v1/klines"
            params = {"symbol": sym, "interval": interval, "startTime": start_time, "endTime": now, "klinePriceType": price_type}
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            klines = []
            for k in data:
                # Mapeamento direto dos campos do dicionário retornado pela Backpack
                klines.append({
                    "start": k.get("start"),
                    "open": k.get("open"),
                    "high": k.get("high"),
                    "low": k.get("low"),
                    "close": k.get("close"),
                    "volume": k.get("volume"),
                    "quoteVolume": k.get("quoteVolume")
                })
            return klines
            

        # --- LÓGICA BINANCE ---
        elif exchange.lower() == "binance":
            
            url = "https://api.binance.com/api/v3/klines"
            params = {"symbol": sym.replace("_", ""), "interval": interval, "endTime": now * 1000, "limit": 1000}
            response = requests.get(url, params=params, timeout=10).json()
            klines = []
            for k in response:
                if len(k) >= 8:  # garante que todos os índices existem
                    klines.append({
                        "start": k[0],
                        "open": k[1],
                        "high": k[2],
                        "low": k[3],
                        "close": k[4],
                        "volume": k[5],
                        "quoteVolume": k[7]
                    })
            return klines

        # --- LÓGICA MEXC ---
        elif exchange.lower() == "mexc":
            clean_sym = sym.replace("_", "")
            try:
                url_spot = "https://api.mexc.com/api/v3/klines"
                params_spot = {"symbol": clean_sym, "interval": interval, "startTime": start_time * 1000, "endTime": now * 1000, "limit": 500}
                data = requests.get(url_spot, params=params_spot, timeout=5).json()
                if isinstance(data, list) and len(data) > 0:
                    return [{"start": k[0], "open": k[1], "high": k[2], "low": k[3], "close": k[4], "volume": k[5], "quoteVolume": k[7]} for k in data]
            except: pass
            
            map_int = {"1m": "Min1", "5m": "Min5", "15m": "Min15", "30m": "Min30", "1h": "Min60", "4h": "Hour4", "1d": "Day1"}
            fut_sym = sym if "_" in sym else f"{sym.replace('USDT','')}_USDT"
            url_fut = f"https://api.mexc.com/api/v1/contract/kline/{fut_sym}"
            resp_fut = requests.get(url_fut, params={"interval": map_int.get(interval, "Min60"), "start": start_time, "end": now}, timeout=10).json()
            if resp_fut.get("success"):
                d = resp_fut["data"]
                return [{"start": d["time"][i]*1000, "open": d["open"][i], "high": d["high"][i], "low": d["low"][i], "close": d["close"][i], "volume": d["vol"][i], "quoteVolume": d["amount"][i]} for i in range(len(d["time"]))]

        # --- LÓGICA GATE.IO ---
        elif exchange.lower() == "gate.io":
            gate_sym = sym if "_" in sym else sym.replace("USDT", "_USDT")
            try:
                url_spot = "https://api.gateio.ws/api/v4/spot/candlesticks"
                params_spot = {"currency_pair": gate_sym, "interval": interval, "from": start_time, "to": now}
                resp = requests.get(url_spot, params=params_spot, timeout=5)
                if resp.status_code == 200:
                    data = resp.json()
                    return [{"start": int(k[0])*1000, "open": k[5], "high": k[3], "low": k[4], "close": k[2], "volume": k[6], "quoteVolume": k[1]} for k in data]
            except: pass

            try:
                url_fut = "https://api.gateio.ws/api/v4/futures/usdt/candlesticks"
                params_fut = {"contract": gate_sym, "interval": interval, "from": start_time, "to": now}
                resp = requests.get(url_fut, params=params_fut, timeout=5)
                if resp.status_code == 200:
                    data = resp.json()
                    return [{"start": int(k['t'])*1000, "open": k['o'], "high": k['h'], "low": k['l'], "close": k['c'], "volume": k['v'], "quoteVolume": k.get('sum', 0)} for k in data]
            except: pass

        # --- LÓGICA VARIATIONAL ---
        elif exchange.lower() == "variational":
            url = "https://omni.variational.io/api/candles"
            
            scraper = cloudscraper.create_scraper() # Cria um scraper que pula Cloudflare
            
            start_iso = datetime.fromtimestamp(start_time, tz=timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.000Z')
            end_iso = datetime.fromtimestamp(now - 1, tz=timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.000Z')
            
            asset = sym.replace("USDT", "").replace("USDC", "").replace("_", "").upper()
            params = {"period": interval, "start": start_iso, "end": end_iso, "cex_asset": asset}
            
            # Usamos scraper.get em vez de requests.get
            resp = scraper.get(url, params=params, timeout=15)
            resp.raise_for_status()
            data = resp.json()
            
            return [{
                "start": k["unix_time_ms"],
                "open": k["open"], "high": k["high"], "low": k["low"],
                "close": k["close"], "volume": k["volume"], "quoteVolume": k["volume"]
            } for k in data]

        elif exchange.lower() == "extended":
            # Mapeamento de intervalos: a Extended usa o padrão ISO 8601 (PT1M, PT1H, etc)
            map_ext = {"1m": "PT1M", "5m": "PT5M", "15m": "PT15M", "1h": "PT1H", "4h": "PT4H", "1d": "P1D"}
            ext_interval = map_ext.get(interval, "PT1H")
            
            # Formata o símbolo (Ex: BTCUSDT -> BTC-USD)
            # A Extended costuma usar o par com USD ou USDC
            clean_sym = sym.replace("_", "-").replace("USDT", "-USD").replace("USDC", "-USD")
            if "-" not in clean_sym: clean_sym = f"{clean_sym}-USD"

            # A URL inclui o símbolo e o tipo de preço na rota
            url = f"https://app.extended.exchange/api/v1/info/candles/{clean_sym}/trades"
            
            params = {
                "interval": ext_interval,
                "limit": 1000,
                "endTime": now * 1000
            }
            
            resp = requests.get(url, params=params, timeout=10)
            if resp.status_code == 200:
                json_data = resp.json()
                if json_data.get("status") == "OK":
                    # Extended retorna: T (timestamp), o (open), h, l, c, v
                    return [{
                        "start": k["T"],
                        "open": k["o"],
                        "high": k["h"],
                        "low": k["l"],
                        "close": k["c"],
                        "volume": k["v"],
                        "quoteVolume": k["v"] # Fallback
                    } for k in json_data["data"]]
    
        elif exchange.lower() == "paradex":
            url = "https://api.prod.paradex.trade/v1/markets/klines"
            
            # Paradex quer resolução em minutos (string)
            map_res = {"1m": "1", "3m": "3", "5m": "5", "15m": "15", "30m": "30", "1h": "60", "4h": "60", "1d": "60"}
            resolution = map_res.get(interval, "60")
            
            # Paradex exige milissegundos (ms)
            p_start_ms = start_time * 1000
            p_now_ms = now * 1000
            
            params = {
                "symbol": sym,
                "resolution": resolution,
                "start_at": p_start_ms,
                "end_at": p_now_ms
            }
            
            resp = requests.get(url, params=params, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            
            # A Paradex retorna uma lista de listas dentro da chave 'results'
            if "results" in data:
                return [{
                    "start": k[0], 
                    "open": k[1], "high": k[2], "low": k[3], "close": k[4], 
                    "volume": k[5], "quoteVolume": k[5]
                } for k in data["results"]]
        
        elif exchange.lower() == "pacifica":
            url = "https://api.pacifica.fi/api/v1/kline"
            
            # Pacifica pede start_time em milissegundos
            params = {
                "symbol": sym.replace("USDT", "").replace("USDC", ""), # Geralmente apenas BTC, ETH
                "interval": interval,
                "start_time": start_time * 1000,
                "end_time": now * 1000
            }
            
            resp = requests.get(url, params=params, timeout=10)
            if resp.status_code == 200:
                json_data = resp.json()
                if json_data.get("success"):
                    # Mapeamento conforme o exemplo: t=time, o=open, h=high, l=low, c=close, v=volume
                    return [{
                        "start": k["t"],
                        "open": k["o"],
                        "high": k["h"],
                        "low": k["l"],
                        "close": k["c"],
                        "volume": k["v"],
                        "quoteVolume": k["v"] # Pacifica não envia quoteVolume explicitamente
                    } for k in json_data["data"]]
    
        elif exchange.lower() == "hyperliquid":
            url = "https://api.hyperliquid.xyz/info"
            
            # Limpa o símbolo: Hyperliquid quer apenas "BTC", "ETH", etc.
            coin = sym.replace("USDT", "").replace("USDC", "").replace("_", "").split("-")[0].upper()
            
            # Corpo da requisição (POST) conforme a documentação
            payload = {
                "type": "candleSnapshot",
                "req": {
                    "coin": coin,
                    "interval": interval,
                    "startTime": start_time * 1000,
                    "endTime": now * 1000
                }
            }
            
            headers = {"Content-Type": "application/json"}
            
            # Note o uso de requests.post em vez de get
            resp = requests.post(url, json=payload, headers=headers, timeout=10)
            
            if resp.status_code == 200:
                data = resp.json()
                # Hyperliquid retorna: t (start), T (end), o (open), h, l, c, v
                return [{
                    "start": k["t"],
                    "open": k["o"],
                    "high": k["h"],
                    "low": k["l"],
                    "close": k["c"],
                    "volume": k["v"],
                    "quoteVolume": k["v"]  # Fallback
                } for k in data]
    
        elif exchange.lower() == "lighter":
            url = "https://mainnet.zklighter.elliot.ai/api/v1/candles"
            
            # Se market_id for passado, usa ele. Se não, tenta usar o sym como ID.
            target_id = market_id if market_id is not None else sym
            
            params = {
                "market_id": target_id,
                "resolution": interval,
                "start_timestamp": start_time * 1000,
                "end_timestamp": now * 1000,
                "count_back": 1500
            }
            resp = requests.get(url, params=params, timeout=10).json()
            if "c" in resp:
                return [{
                    "start": k["t"], "open": k["o"], "high": k["h"], 
                    "low": k["l"], "close": k["c"], "volume": k["v"], 
                    "quoteVolume": k.get("V", k["v"])
                } for k in resp["c"]]
        
        elif exchange.lower() == "nado":
            # Endpoint fictício baseado na doc (substitua pela URL correta da Nado se necessário)
            url = "https://archive.prod.nado.xyz/v1" # Verifique o endpoint exato de POST
            
            # Mapeamento de intervalo para segundos
            map_gran = {"1m": 60, "5m": 300, "15m": 900, "1h": 3600, "4h": 14400, "1d": 86400}
            granularity = map_gran.get(interval, 3600)
            
            # Nado usa product_id. Usaremos o market_id passado no teste.
            target_id = market_id if market_id is not None else 1
            
            payload = {
                "candlesticks": {
                    "product_id": target_id,
                    "max_time": now, # 'now' já está em segundos no topo da função
                    "limit": 1500,
                    "granularity": granularity
                }
            }
            
            resp = requests.post(url, json=payload, timeout=10)
            
            if resp.status_code == 200:
                json_data = resp.json()
                # Precisamos dividir os campos _x18 por 10^18
                factor = 10**18
                return [{
                    "start": int(k["timestamp"]) * 1000, # Converter segundos para ms
                    "open": float(k["open_x18"]) / factor,
                    "high": float(k["high_x18"]) / factor,
                    "low": float(k["low_x18"]) / factor,
                    "close": float(k["close_x18"]) / factor,
                    "volume": float(k["volume"]) / factor,
                    "quoteVolume": float(k["volume"]) / factor
                } for k in json_data["candlesticks"]]
    
    except Exception as e:
        print(f"❌ Erro na exchange {exchange} para {sym}: {e}")
        return []
    return []