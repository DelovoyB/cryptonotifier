from fastapi import FastAPI, HTTPException, Depends, Request, Form
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql://root:root@postgres/alerts"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


class CryptoAlert(Base):
    __tablename__ = "crypto_alerts"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True)
    convert = Column(String)
    price = Column(Float)


def init_db():
    Base.metadata.create_all(bind=engine)


app = FastAPI()


@app.on_event("startup")
def on_startup():
    init_db()


@app.post("/alerts/")
async def create_alert(request: Request):
    try:
        data = await request.json()
        symbol = data.get("symbol")
        convert = data.get("convert")
        price = data.get("price")
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid input format")

    if not symbol or not convert or price is None:
        raise HTTPException(status_code=400, detail="Missing required fields")

    db = SessionLocal()
    db_alert = CryptoAlert(symbol=symbol, convert=convert, price=price)
    db.add(db_alert)
    db.commit()
    db.refresh(db_alert)
    db.close()

    return db_alert