from celery import Celery
from celery.schedules import crontab
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import requests
import os
import json

from main import CryptoAlert

CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://redis:6379/0")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://redis:6379/0")

celery_app = Celery('tasks', broker=CELERY_BROKER_URL, backend=CELERY_RESULT_BACKEND)

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://root:root@postgres/alerts")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

API_URL = "http://crypto-api:8000/price"

try:
    CryptoAlert.__table__.create(bind=engine, checkfirst=True)
except OperationalError:
    pass


@celery_app.task
def check_prices():
    db = SessionLocal()
    alerts = db.query(CryptoAlert).all()

    for alert in alerts:
        response = requests.get(API_URL, params={'symbol': alert.symbol, 'convert': alert.convert})
        data = response.json()
        print(f'{alert.symbol=}, {alert.convert=}, {alert.price=}', data)
        current_price = data.get('price')

        if current_price and current_price < alert.price:
            send_telegram_notification(alert.symbol, alert.convert, current_price)

    db.close()


def send_telegram_notification(symbol, convert, current_price):
    telegram_token = os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    message = f"The price of {symbol}/{convert} has dropped to {current_price}!"

    url = f"https://api.telegram.org/bot{telegram_token}/sendMessage"
    payload = {"chat_id": chat_id, "text": message}
    headers = {"Content-Type": "application/json"}

    requests.post(url, data=json.dumps(payload), headers=headers)


@celery_app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(crontab(minute='*/1'), check_prices.s())
