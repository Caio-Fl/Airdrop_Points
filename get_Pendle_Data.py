def get_Pendle_Data(marketAdd,tokenAdd):
    # Importar Bibliotecas Python
    import requests
    import json

    # Inicialização
    #url = "https://api-v2.pendle.finance/core/v2/1/markets/0xa77c0de4d26b7c97d1d42abd6733201206122e25/data" # endereço base de request dos dados
    #url = "https://api-v2.pendle.finance/core/v1/sdk/1/markets/0xe45d2ce15abba3c67b9ff1e7a69225c855d3da82/swapping-prices"
    #url = "https://api-v2.pendle.finance/core/v2/1/markets/0xe45d2ce15abba3c67b9ff1e7a69225c855d3da82/data"
    #url = "https://api-v2.pendle.finance/core/v1/1/markets/0xe45d2ce15abba3c67b9ff1e7a69225c855d3da82"
    #url = "https://api-v2.pendle.finance/core/v1/dashboard/positions/database/0x75d85ca4971625b8f179E3d39Cd4aA72bE2c6D4B" #pega posição da sua wallet dentro da pendle
    #levelMarketAdd = 0xe45d2ce15abba3c67b9ff1e7a69225c855d3da82
    #levelTokenAdd = 0x65901Ac9EFA7CdAf1Bdb4dbce4c53B151ae8d014
    # leitura
    url = f"https://api-v2.pendle.finance/core/v1/1/markets/{marketAdd}"
    response = requests.get(url)
    jsonn = json.loads(response.text)
    #jsonn.get("underlyingApy", {}) 
    unApy = jsonn.get("underlyingApy", {})
    impApy = jsonn.get("impliedApy", {})
    feeRate = jsonn.get("extendedInfo", {}).get("feeRate", "0")
    swapFee = jsonn.get("swapFeeApy", {})
    ytRoi = jsonn.get("ytRoi", {})
    expiry = jsonn.get("expiry", {})
    
    url = f"https://api-v2.pendle.finance/core/v1/sdk/1/markets/{marketAdd}/swapping-prices"
    response = requests.get(url)
    jsonn = json.loads(response.text)
    ytMultiplier = jsonn.get("underlyingTokenToYtRate", {})

    url = f"https://api-v2.pendle.finance/core/v1/sdk/1/markets/{marketAdd}/swap?receiver=0xa5604bBEccd7b00e3B834cBa26Cf876D3d175d83&slippage=0.05&enableAggregator=true&tokenIn=0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48&tokenOut={tokenAdd}&amountIn=1000000000&additionalData=effectiveApy"
    response = requests.get(url)
    jsonn = json.loads(response.text)
    priceImpact = jsonn.get("data", {}).get("priceImpact", "0")
    #ytMultiplier = int(jsonn.get("data", {}).get("amountOut", "0"))/1000000000000000000/1000
  
    return(ytMultiplier,unApy,impApy,feeRate,swapFee,ytRoi,expiry,priceImpact)