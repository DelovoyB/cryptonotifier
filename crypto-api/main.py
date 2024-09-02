from fastapi import FastAPI, HTTPException, Query, Request
from pydantic import BaseModel
from requests import Session
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

API_URL = "https://pro-api.coinmarketcap.com/v2/tools/price-conversion"

headers = {
  'Accepts': 'application/json',
  'X-CMC_PRO_API_KEY': os.getenv("API_KEY"),
}


class CryptoRequest(BaseModel):
    symbol: str
    convert: str


@app.get("/price")
async def get_price(
    symbol: str = Query(None),
    convert: str = Query(None)
):
    if symbol is None or convert is None:
        raise HTTPException(status_code=400, detail="Missing query parameters")

    session = Session()
    session.headers.update(headers)

    params = {
        "amount": 1,
        "symbol": symbol,
        "convert": convert,
    }
    print(params)
    try:
        response = session.get(API_URL, params=params)

        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Failed to fetch data")

        data = response.json()

        price = round(data['data'][0]['quote'][convert]['price'], 2)
        return {"price": price}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/price")
async def post_price(request: CryptoRequest):
    try:
        symbol = request.symbol
        convert = request.convert

        if symbol is None or convert is None:
            raise HTTPException(status_code=400, detail="Missing parameters")

        session = Session()
        session.headers.update(headers)

        params = {
            "amount": 1,
            "symbol": symbol,
            "convert": convert,
        }
        print(params)
        response = session.get(API_URL, params=params)

        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Failed to fetch data")

        data = response.json()

        price = round(data['data'][0]['quote'][convert]['price'], 2)
        return {"price": price}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
