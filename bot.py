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

def get_last_trade_price(instrument_name):
    """Obtém o último preço de negociação (last trade price) de um instrumento."""
    method = 'public/get-trades'
    params = {"instrument_name": instrument_name, "count": 1}
    
    # A API de dados públicos é diferente, mas para simplificar, usaremos a mesma função make_request
    # com a ressalva de que a assinatura não é estritamente necessária para endpoints públicos,
    # mas a estrutura da requisição da Crypto.com exige a assinatura mesmo para alguns endpoints públicos.
    # No entanto, o endpoint 'public/get-trades' é público e não requer autenticação.
    # Vamos criar uma função separada para requisições públicas para maior clareza.
    
    public_url = 'https://api.crypto.com/exchange/v1/public/'
    
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'Python Crypto.com API Client'
    }
    
    request_data = {
        'id': 1,
        'method': method,
        'params': params,
        'nonce': int(time.time() * 1000)
    }
    
    try:
        response = requests.post(public_url + method.replace('public/', ''), json=request_data, headers=headers)
        response.raise_for_status()
        data = response.json()
        if data['code'] == 0 and data['result']['data']:
            # O último trade é o primeiro da lista
            return float(data['result']['data'][0]['p'])
        else:
            print(f"Falha ao obter o último preço de negociação: {data}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Erro na requisição pública: {e}")
        return None

def get_historical_trades(instrument_name, count=100):
    """Obtém o histórico de trades do usuário."""
    print(f"Obtendo histórico de trades para {instrument_name}...")
    params = {"instrument_name": instrument_name, "page_size": count}
    response = make_request('private/get-trades', params)
    if response and response['code'] == 0:
        print(f"Histórico de Trades para {instrument_name}:")
        if response['result']['trade_list']:
            for trade in response['result']['trade_list']:
                print(f"  ID: {trade['trade_id']}, Lado: {trade['side']}, Preço: {trade['price']}, Quantidade: {trade['quantity']}, Tempo: {trade['create_time']}")
            return response['result']['trade_list']
        else:
            print("  Nenhum trade encontrado.")
            return []
    else:
        print("Falha ao obter histórico de trades.")
        print(response)
        return []

def get_last_buy_price(instrument_name):
    """Encontra o preço da última ordem de COMPRA executada."""
    trades = get_historical_trades(instrument_name, count=50) # Busca os últimos 50 trades
    for trade in trades:
        if trade['side'] == 'BUY':
            return float(trade['price'])
    return None

def trading_strategy(instrument_name, quantity, profit_percentage=0.01):
    """
    Estratégia de Compra e Venda Automática:
    1. Se não houver posição de compra anterior, compra ao preço de mercado.
    2. Se houver uma posição de compra, calcula o preço de venda com lucro (profit_percentage).
    3. Coloca uma ordem de venda de limite no preço calculado.
    """
    print(f"\n--- Executando Estratégia de Trading para {instrument_name} ---")
    
    # 1. Obter o último preço de negociação
    current_price = get_last_trade_price(instrument_name)
    if not current_price:
        print("Não foi possível obter o preço atual. Abortando estratégia.")
        return

    # 2. Obter o preço da última compra
    last_buy_price = get_last_buy_price(instrument_name)

    if last_buy_price is None:
        # Não há posição de compra anterior, então COMPRA
        print(f"Nenhuma compra anterior encontrada. Preparando para COMPRAR {quantity} de {instrument_name} ao preço de mercado ({current_price}).")
        
        # Para simplificar e evitar complexidades de ordens de mercado, usaremos uma ordem de limite
        # ligeiramente acima do preço atual para garantir a execução rápida (simulando mercado).
        # Em um robô real, usaríamos uma ordem de mercado ou uma ordem de limite no preço bid/ask.
        buy_price = current_price * 1.0001 # Preço ligeiramente acima para simular execução rápida
        
        # Colocar ordem de COMPRA
        place_limit_order(instrument_name, 'BUY', buy_price, quantity)
        
    else:
        # Há uma posição de compra anterior, então VENDE com lucro
        profit_price = last_buy_price * (1 + profit_percentage)
        
        print(f"Última compra em: {last_buy_price}. Preço de lucro ({profit_percentage*100}%): {profit_price:.8f}")
        print(f"Preço atual: {current_price}")

        if current_price >= profit_price:
            # O preço atual atingiu ou superou o preço de lucro, então VENDE
            print(f"Preço de lucro atingido! Preparando para VENDER {quantity} de {instrument_name} ao preço de mercado ({current_price}).")
            
            # Para simplificar, usaremos uma ordem de limite ligeiramente abaixo do preço atual
            sell_price = current_price * 0.9999 # Preço ligeiramente abaixo para simular execução rápida
            
            # Colocar ordem de VENDA
            place_limit_order(instrument_name, 'SELL', sell_price, quantity)
        else:
            print("Preço de lucro ainda não atingido. Aguardando...")

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
    # --- Configurações do Robô ---
    INSTRUMENT = 'BTC_USDT' # Par de negociação
    QUANTITY = 0.0001       # Quantidade a ser negociada (ajuste conforme o mínimo da corretora)
    PROFIT_PERCENTAGE = 0.01 # 1% de lucro
    RUN_INTERVAL_SECONDS = 60 # Intervalo de execução da estratégia (em segundos)
    
    print("Robô de trading de criptomoedas inicializado.")
    print("Por favor, configure suas chaves de API no arquivo .env.")
    
    # Exemplo de uso da estratégia de trading
    # O robô deve ser executado em um loop infinito em um ambiente de produção.
    # Para fins de demonstração, executaremos a estratégia uma vez.
    
    # Descomente o loop abaixo para simular a execução contínua:
    # while True:
    #     trading_strategy(INSTRUMENT, QUANTITY, PROFIT_PERCENTAGE)
    #     time.sleep(RUN_INTERVAL_SECONDS)
    
    # Execução única para demonstração:
    trading_strategy(INSTRUMENT, QUANTITY, PROFIT_PERCENTAGE)
    
    # Funções de exemplo que podem ser usadas para monitoramento:
    # get_account_summary()
    # get_open_orders(INSTRUMENT)
    # cancel_order(INSTRUMENT, 'SEU_ORDER_ID') # Substitua SEU_ORDER_ID pelo ID da ordem real

