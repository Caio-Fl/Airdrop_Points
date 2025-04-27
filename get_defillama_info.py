def get_defillama_info(protocol,network):
    # Import Biblioteca
    import requests
    import json

    url = f"https://api.llama.fi/updatedProtocol/{protocol}"
    response = requests.get(url)
    data = response.json()
    tvl = round((data.get("currentChainTvls", []).get(network, []))/1000000,3)
    try:
        raises = data.get("raises", [{}])
        amount = raises[0].get("amount", [])
        leadInvestors = raises[0].get("leadInvestors", [])
        otherInvestors = raises[0].get("otherInvestors", [])
    except:
        amount = "No Info"
        leadInvestors = "No Info"
        otherInvestors = "No Info"
    
    
    return(tvl,amount,leadInvestors,otherInvestors)