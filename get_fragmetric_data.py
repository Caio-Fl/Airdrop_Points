def get_fragmetric_data():

    # Importar Bibliotecas Python
    import requests
    import json
    import time
    from datetime import datetime, timezone, timedelta

    headers = {
            "path": "/v1/graphql",
            "Content-Type": "application/json",
            "Accept": "*/*"
    }

    payload = {"operationName":"restakingFund","variables":{},"extensions":{"persistedQuery":{"version":1,"sha256Hash":"ea2749c76bda5b889a1e5b9c5958b9aa6e027d009b71fab8b2a1bff4e4eedc71"}}}
    url = f"https://api.fragmetric.xyz/v1/graphql"
    response = requests.post(url, json=payload, headers=headers)
    data = response.json()
    jsonn = json.loads(response.text)

    solAsUSD = float(data.get("data", {}).get("solAsUSD", "0"))
    fragAPYarray = data.get("data", {}).get("restakingFunds", [{}])
    fragAPY = float(fragAPYarray[0].get("receiptToken", {}).get("metadata", {}).get("apy", {}))
    fragAsUSD = float(fragAPYarray[0].get("receiptToken", {}).get("metadata", {}).get("oneTokenAsUSD", {}))
    fragBySol = fragAsUSD/solAsUSD


    payload = {"operationName":"fPointEstimations","variables":{},"extensions":{"persistedQuery":{"version":1,"sha256Hash":"423082c3bd12d59281c0463274f998270efa80af1316ed7647a51ee85be536f1"}}}
    url = f"https://api.fragmetric.xyz/v1/graphql"
    response = requests.post(url, json=payload, headers=headers)
    data2 = response.json()
    total = data2.get("data", {}).get("fPointEstimations", {}).get("totalAccrualAmount", "0")
    total_users = data2.get("data", {}).get("fPointEstimations", {}).get("usersCount", "0")
    total_accured = round(float(total)/10000,0)
    return(total_accured,fragAPY,solAsUSD,fragAsUSD,fragBySol,total_users)