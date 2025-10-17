import os
import time
import hmac
import hashlib
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv('CRYPTOCOM_API_KEY')
SECRET_KEY = os.getenv('CRYPTOCOM_SECRET_KEY')
BASE_URL = 'https://api.crypto.com/exchange/v1/private/'

def generate_signature(api_key, secret_key, method, params, nonce):
    payload_str = method + str(nonce) + api_key
    if params:
        for key in sorted(params.keys()):
            payload_str += str(params[key])
    
    sig = hmac.new(bytes(secret_key, 'utf-8'), msg=bytes(payload_str, 'utf-8'), digestmod=hashlib.sha256).hexdigest()
    return sig

def make_request(method, params=None):
    if params is None:
        params = {}
    
    nonce = int(time.time() * 1000)
    signature = generate_signature(API_KEY, SECRET_KEY, method, params, nonce)

    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'Python Crypto.com API Client'
    }

    request_data = {
        'id': 1,
        'method': method,
        'api_key': API_KEY,
        'params': params,
        'nonce': nonce,
        'sig': signature
    }

    try:
        response = requests.post(BASE_URL + method.replace('private/', ''), json=request_data, headers=headers)
        response.raise_for_status()  # Raise an exception for HTTP errors
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Erro na requisição: {e}")
        return None

def get_account_summary():
    print("Obtendo resumo da conta...")
    response = make_request('private/get-account-summary')
    if response and response['code'] == 0:
        print("Resumo da Conta:")
        for account in response['result']['accounts']:
            print(f"  Moeda: {account['currency']}, Saldo: {account['balance']}, Disponível: {account['available']}")
    else:
        print("Falha ao obter resumo da conta.")
        print(response)

def get_open_orders(instrument_name):
    print(f"Obtendo ordens abertas para {instrument_name}...")
    params = {"instrument_name": instrument_name}
    response = make_request('private/get-open-orders', params)
    if response and response['code'] == 0:
        print(f"Ordens Abertas para {instrument_name}:")
        if response['result']['order_list']:
            for order in response['result']['order_list']:
                print(f"  ID da Ordem: {order['order_id']}, Preço: {order['price']}, Quantidade: {order['quantity']}, Lado: {order['side']}")
        else:
            print("  Nenhuma ordem aberta encontrada.")
    else:
        print("Falha ao obter ordens abertas.")
        print(response)

def place_limit_order(instrument_name, side, price, quantity):
    print(f"Colocando ordem {side} de limite para {instrument_name}...")
    params = {
        "instrument_name": instrument_name,
        "side": side,
        "type": "LIMIT",
        "price": price,
        "quantity": quantity
    }
    response = make_request('private/create-order', params)
    if response and response['code'] == 0:
        print(f"Ordem de limite {side} para {instrument_name} colocada com sucesso. ID da Ordem: {response['result']['order_id']}")
    else:
        print("Falha ao colocar ordem de limite.")
        print(response)

def cancel_order(instrument_name, order_id):
    print(f"Cancelando ordem {order_id} para {instrument_name}...")
    params = {
        "instrument_name": instrument_name,
        "order_id": order_id
    }
    response = make_request('private/cancel-order', params)
    if response and response['code'] == 0:
        print(f"Ordem {order_id} cancelada com sucesso.")
    else:
        print("Falha ao cancelar ordem.")
        print(response)

if __name__ == "__main__":
    # Exemplo de uso (substitua com seus próprios valores)
    # get_account_summary()
    # get_open_orders('BTC_USDT')
    # place_limit_order('BTC_USDT', 'BUY', 60000, 0.0001) # Exemplo: Comprar 0.0001 BTC a 60000 USDT
    # cancel_order('BTC_USDT', 'SEU_ORDER_ID') # Substitua SEU_ORDER_ID pelo ID da ordem real
    print("Robô de trading de criptomoedas inicializado. As funções estão comentadas para evitar execuções acidentais.")
    print("Por favor, configure suas chaves de API no arquivo .env e descomente as funções para testar.")

