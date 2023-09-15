from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from flask_socketio import SocketIO
from flask_cors import CORS
import ssl
from celery import Celery
import json
import ccxt
from crypto.dataStream_price import generateSession,sendMessage,sendPingPacket,socketJob
from websocket import create_connection
from crypto.crypto_indicators import Indicator2,logger
import time
from flask_httpauth import HTTPBasicAuth

auth2 = HTTPBasicAuth()

@auth2.verify_password
def verify_password(username,password):
    if password == '526af4fbd93bc393a6392db7':
        return True
    return False

def make_celery(app):
    celery = Celery(
        'trading_bots',
        backend='redis://127.0.0.1:6379',
        broker='redis://127.0.0.1:6379',
        task_default_queue='bot_queue',  # Set a specific queue for the task
        #task_default_delivery_mode='transient',  # Make the task transient to prevent persistence
        #worker_concurrency=10,  # Limit the worker concurrency to 1
    )

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery

app = Flask(__name__, template_folder="templates")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///crypto.db"
app.config["SQLALCHEMY_TRACK_MODIFICATION"] = False
app.config['SESSION_PERMANENT'] = True
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] ='2odabahaa@gmail.com'
app.config['MAIL_PASSWORD'] = 'mzdkqpflejakjled'



celery = make_celery(app)


# Create an SSL context
context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
context.load_cert_chain('cert.pem', 'key.pem')

mail = Mail(app)
app.config["SECRET_KEY"] = "526af4fbd93bc393a6392db7"
db = SQLAlchemy(app)

socketio = SocketIO(app, async_mode='threading')
socketio.init_app(app, cors_allowed_origins="*")
cors = CORS(app)

# Initialize Flask-Login's LoginManager
login_manager = LoginManager(app)
login_manager.login_view = 'login'



#run routes folder
from crypto import auth
from crypto import routes
from crypto import notify
from crypto import data
from crypto import notify
from crypto import gpt
from crypto import transactions
from crypto import smartTrade
from crypto import orders
from crypto import bots

'''@celery.task
def update_symbol_data(symbol,intervals,exchange):
    indicator = Indicator(
        exchange=exchange, 
        pair=symbol,
        intervals=intervals,
        verbose=0
    )
    try:
        indicators = indicator.update_data()
        for interval in intervals:
            with open(f"stochData/stoch_{symbol.replace('/', '').replace('.D', '', 1).replace('.T', '', 1)}_{interval}_{exchange}.json", 'w') as f:
                json.dump(indicators[interval][exchange].to_dict(orient='records'), f)
        
        symbol_name = symbol.replace('/', '').replace('.D', '', 1).replace('.T', '', 1)
        with open(f"24changes/{symbol.replace('/', '').replace('.D', '', 1).replace('.T', '', 1)}_{exchange}.json", 'w') as f:
            json.dump(changes.to_dict(orient='records'), f)

        with open(f"24changes/{symbol.replace('/', '').replace('.D', '', 1).replace('.T', '', 1)}_{exchange}.json", 'r') as f:
            changes = json.load(f)
            # Calculate the percentage change between the opening and closing prices over the past 24 hours
            last_open = changes[-1]['open']
            last_close = changes[-1]['close']
            price_change = (last_close - last_open) / last_open * 100

            # Calculate the percentage change between the opening and closing prices from 24 hours ago
            last_close = changes[-1]['close']
            first_close = changes[0]['close']                
            percent_change_24h = (last_close - first_close) / first_close * 100

        try:
            with open("pricesData/"+f"{exchange.replace('okex','okx').upper()}{symbol_name}.json".replace("/","").replace(".D","",1).replace(".T","",1), "r") as f:
                existing_data = json.load(f)
                existing_data[f"{exchange.replace('okex','okx').upper()}:{symbol_name}"][4] = price_change
                existing_data[f"{exchange.replace('okex','okx').upper()}:{symbol_name}"][6] = percent_change_24h

                # write updated data to JSON file
                with open("pricesData/"+f"{exchange.replace('okex','okx').upper()}{symbol_name}.json".replace("/","").replace(".D","",1).replace(".T","",1), "w") as f:
                    json.dump(existing_data, f)
                    
        except FileNotFoundError:
            existing_data = {}

    except Exception as e:
        logger.exception(e)
    '''

@celery.task
def update_price_data(symbols,exchange):
    while True:
        start_time = time.time()
        for symbol in symbols:
            exchange = exchange.replace('okex','okx').upper()
            symbol_id = f"{exchange}:{symbol.replace('/', '')}"
            tradingViewSocket = "wss://data.tradingview.com/socket.io/websocket"
            headers = json.dumps({"Origin": "https://data.tradingview.com"})
            ws = create_connection(tradingViewSocket, headers=headers)
            session = generateSession()

            # Send messages
            sendMessage(ws, "quote_create_session", [session])
            sendMessage(ws, "quote_set_fields", [session, "lp"])
            sendMessage(ws, "quote_add_symbols", [session, symbol_id])

            # Start job
            price = socketJob(ws,symbol_id,tradingViewSocket,headers)
            symbol_name = f"{exchange}"+symbol.replace('/', '')
            try:
                with open("pricesData/"+f"{symbol_name}.json".replace("/","").replace(".D","",1).replace(".T","",1), 'r') as f:
                    data2 = json.load(f)
            except FileNotFoundError:
                data = {}
                with open("pricesData/"+f"{symbol_name}.json".replace("/","").replace(".D","",1).replace(".T","",1), 'w') as f:
                    json.dump(data, f)

            data = {symbol: [price,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]}
            print(symbol_id)
            print("------------********------------------")
            print(price)
            # check if symbol already exists in the JSON file
            try:
                with open("pricesData/"+f"{symbol_name}.json".replace("/","").replace(".D","",1).replace(".T","",1), "r") as f:
                    existing_data = json.load(f)
            except FileNotFoundError:
                existing_data = {}
            if symbol in existing_data:
                # update symbol value
                existing_data[symbol][0] = price
            else:
                # add symbol to JSON file
                existing_data.update(data)

            # write updated data to JSON file
            with open("pricesData/"+f"{symbol_name}.json".replace("/","").replace(".D","",1).replace(".T","",1), "w") as f:
                json.dump(existing_data, f)

        print(f"Elapsed time (update_price_data): {time.time() - start_time} seconds")
        time.sleep(1)

@celery.task
def update_volume_data(symbols,exchange):
    while True:
        start_time = time.time()
        for symbol in symbols:
            # Start job
            x = getattr(ccxt, exchange)().fetch_ticker(symbol)
            volume = x['baseVolume']
            turnover = x['quoteVolume']
            high = x['high']
            low = x['low']
            percentage = x['percentage']
            change = x['change']
            symbol_name = f"{exchange}"+symbol.replace('/', '')
            try:
                with open("volumesData/"+f"{symbol_name}.json".replace("/","").replace(".D","",1).replace(".T","",1), 'r') as f:
                    data2 = json.load(f)
            except FileNotFoundError:
                data = {}
                with open("volumesData/"+f"{symbol_name}.json".replace("/","").replace(".D","",1).replace(".T","",1), 'w') as f:
                    json.dump(data, f)

            data = {symbol: [volume,turnover,high,low,percentage,change]}

            # check if symbol already exists in the JSON file
            try:
                with open("volumesData/"+f"{symbol_name}.json".replace("/","").replace(".D","",1).replace(".T","",1), "r") as f:
                    existing_data = json.load(f)
            except FileNotFoundError:
                existing_data = {}
            if symbol in existing_data:
                # update symbol value
                existing_data[symbol][0] = volume
                existing_data[symbol][1] = turnover
                existing_data[symbol][2] = high
                existing_data[symbol][3] = low
                existing_data[symbol][4] = percentage
                existing_data[symbol][5] = change
            else:
                # add symbol to JSON file
                existing_data.update(data)

            # write updated data to JSON file
            with open("volumesData/"+f"{symbol_name.replace('okex','okx').upper()}.json".replace("/","").replace(".D","",1).replace(".T","",1), "w") as f:
                json.dump(existing_data, f)

        time.sleep(1)
        print(f"Elapsed time (update_volume_data): {time.time() - start_time} seconds")

@celery.task
def update_symbol_indicator(symbols,exchange):
    while True:
        start_time = time.time()
        for symbol in symbols:
            for interval in ["1m","3m","5m","15m","30m","1h","2h","4h","6h","12h","1d","1w"]:
                indicator = Indicator2(
                    exchange=exchange, 
                    pair=symbol,
                    interval=interval,
                    verbose=0
                )
                try:
                    indicators_data = indicator.update_data()
                    file_name_stoch = f"stochData/stoch_{symbol.replace('/', '').replace('.D', '', 1).replace('.T', '', 1)}_{interval}_{exchange}.json"
                    with open(file_name_stoch, 'w') as f:
                        json.dump(indicators_data[interval].to_dict(orient='records'), f)
                except Exception as e:
                    logger.exception(e)
        time.sleep(1)
        print(f"Elapsed time (update_symbol_indicator): {time.time() - start_time} seconds")

exchanges = ['okex']

@app.route('/start_data_stream')
@auth2.login_required
def run_data_stream():
    routes.bot_func_all.delay()
    routes.smart_trade_bot_all.delay()
    for exchange in exchanges:
        pairs = []
        pairs2 = []
        for currency in getattr(ccxt, exchange)().fetch_markets():
            if currency['spot']:
                pairs2.append(currency['symbol'])
            if currency['spot'] and ('USDT' in currency['symbol']):
                pairs.append(currency['symbol'])

        chunk_size = 10
        chunk_size2 = 50

        for i in range(0, int(len(pairs)/chunk_size)):
            update_volume_data.delay(pairs[i*50:(i+1)*50], exchange)
            update_price_data.delay(pairs[i*chunk_size:(i+1)*chunk_size], exchange)

        for i in range(0, int(len(pairs2)/chunk_size2)):
            update_symbol_indicator.delay(pairs2[i*chunk_size2:(i+1)*chunk_size2], exchange)
            pass
            
    return "runned"

@app.route('/stop_data_stream')
@auth2.login_required
def stop_data_stream():
    task_names = ['update_price_data', 'update_symbol_indicator','smart_trade_bot_all','bot_func_all']

    # Inspect active tasks
    i = celery.control.inspect()
    active_tasks = i.active()

    # Revoke tasks with matching names
    for worker, tasks in active_tasks.items():
        for task in tasks:
            if task['name'] in task_names:
                celery.control.revoke(task['id'])

    return "stopped"



