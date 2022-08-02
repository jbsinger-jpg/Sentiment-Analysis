import requests, json
from config import *
BASE_URL = "https://paper-api.alpaca.markets"
ACCOUNT_URL = "{}/v2/account".format(BASE_URL)
ORDERS_URL = "{}/v2/orders".format(BASE_URL)
HEADERS = {"APCA-API-KEY-ID": ALPACA_CLIENT_ID,
           "APCA-API-SECRET-KEY": ALPACA_SECRET}


def get_account():
    r = requests.get(ACCOUNT_URL, headers=HEADERS)
    return json.loads(r.content)


def create_order(symbol, quantity, side, type_of_order, time_in_force, client_order_id):
    data = {
        "symbol": symbol,
        "qty": quantity,
        "side": side,
        "type": type_of_order,
        "time_in_force": time_in_force,
        "client_order_id": client_order_id
    }
    r = requests.post(ORDERS_URL, json=data, headers=HEADERS)
    return json.loads(r.content)
