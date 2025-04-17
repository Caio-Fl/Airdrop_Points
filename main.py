from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

# Modelo de dados esperado no POST
class ScalarData(BaseModel):
    tag: str
    value: float

# Endpoint para receber dados escalares via POST
@app.post("/dados")
async def receber_dado(data: ScalarData):
    print(f"Recebido: {data.tag} = {data.value}")
    return {
        "status": "ok",
        "tag": data.tag,
        "value": data.value
    }

# Instruções:
# 1. Execute com: uvicorn main:app --reload --port 8000
# 2. Envie dados com requests.post("http://localhost:8000/dados", json={"tag": "temperatura", "value": 25.3})
