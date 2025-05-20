def get_Leader_Spark_Data():
    # Importar Bibliotecas Python
    import requests
    import json

    top100 = 0
    url = "https://spark2-api.blockanalitica.com/api/pendle/04dc2eb0-dd58-4b2a-9ff0-7c883b7957c5/?order=-total_points&p=1&p_size=100"
    response = requests.get(url)
    if response.status_code == 200:

        data = json.loads(response.text)
        count = data.get("count", [])
        total_accured = round(float(data.get("total_tokens",[])),2)
        tokens_per_sec = data.get("tokens_per_second",{})
        tokens_per_day = float(tokens_per_sec) * 86400 * 1000000
        leaderdoard = data.get("",[])
        for entry in data["results"][:100]:  # Pega apenas os 100 primeiros
            total_points = float(entry["total_points"])
            top100 += total_points

    else:
        print(f"Erro ao coletar dados na página {page}. Status Code:", response.status_code)
        
    top100p = top100/total_accured

    return(total_accured,top100p,count,tokens_per_day)
