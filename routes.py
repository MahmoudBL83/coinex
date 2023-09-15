import json
from flask import render_template, request, redirect, url_for, jsonify,Response
import ccxt
from flask_login import login_required,current_user
from crypto import app,db,socketio,celery
from crypto.models import User, Exchange, Post, Category
from crypto.notify import send_notification
from crypto.dataStream_indicators import update_symbol_data,calculate_signals
from search_crypto import search
from crypto.exchanges import connectExchange
from crypto.functions import getPrice

@app.route("/drop_all/")
def drop_all():
    db.drop_all()
    return jsonify("dropped")

@app.route("/create_all/")
def create_all():
    db.create_all()
    for x in ['news','updates','announcements','general','trading','technical','fundamental','other']:
        db.session.add(Category(title=x))
    db.session.commit()
    return jsonify("created")

################################################Dashboard##############################################################

@app.route("/dashboard/")
@login_required
def dashboard():
    if current_user.exchanges.filter(Exchange.isActive==True).first() is None:
        return redirect(url_for('exchanges'))
    
    exchange_name = current_user.exchanges.filter(Exchange.isActive==True).first().name
    # Initialize CCXT exchange object
    exchange = connectExchange(exchange_name)
    current_user.update_balance()

    assets_json = []

    for exchange_user in current_user.exchanges.all():
        api_key,api_secret,password = exchange_user.get_creds()
        if password:
            exchangeForUser = getattr(ccxt, exchange_user.name)({
                'apiKey': api_key,
                'secret': api_secret,
                'password':password,
            })
        else:
            exchangeForUser = getattr(ccxt, exchange_user.name)({
                'apiKey': api_key,
                'secret': api_secret,
            })
        if exchange_user.demo:
            exchangeForUser.set_sandbox_mode(True)

        assets = exchangeForUser.fetch_balance()
        for asset, amount in assets["total"].items():
            price = getPrice(exchangeForUser.name,asset+'/USDT')
            if not price:
                price = 0
            if check_assets_json(assets_json, asset):
                for asset_json in assets_json:
                    if asset_json['currency'] == asset:
                        asset_json['free'] += assets["free"][asset]
                        asset_json['used'] += assets["used"][asset]
                        asset_json['total'] += amount
                        asset_json['eqUSD'] += amount*price
            else:
                assets_json.append({"currency":asset,"free":assets["free"][asset],"used":assets["used"][asset],"total":amount,"price":price,'eqUSD':amount*price})

    transactions = []
    open_orders = exchange.fetch_open_orders()
    for exchange_user in current_user.exchanges:
        api_key,api_secret,password = exchange_user.get_creds()
        if password:
                exchangeNow = getattr(ccxt, exchange_user.name)({
                    'apiKey': api_key,
                    'secret': api_secret,
                    'password':password,
                })
        else:
            exchangeNow = getattr(ccxt, exchange_user.name)({
                'apiKey': api_key,
                'secret': api_secret,
            })
        if exchange_user.demo:
            exchangeNow.set_sandbox_mode(True)

        for trans in exchangeNow.fetch_ledger():
            trans['exchange'] = exchange_user.name
            transactions.append(trans)
            
    return render_template("dashboard.html",
                                assets=assets_json,
                                balance_usd = current_user.balance_usd,
                                balance_btc = current_user.balance_btc,
                                balance_history = json.dumps([bal.serialize() for bal in current_user.balance_history]),
                                exchanges=current_user.exchanges.all(),
                                open_orders=open_orders,
                                transactions= transactions,
                                profit_monthly_btc=current_user.profit_monthly_btc,
                                profit_monthly_usd=current_user.profit_monthly_usd,
                                profit_daily_btc = current_user.profit_daily_btc,
                                profit_daily_usd = current_user.profit_daily_usd,
                                profit_monthly_percent_btc = current_user.profit_monthly_percent_btc,
                                profit_monthly_percent_usd = current_user.profit_monthly_percent_usd,
                                profit_daily_percent_btc = current_user.profit_daily_percent_btc,
                                profit_daily_percent_usd = current_user.profit_daily_percent_usd,
                                profit_overall_btc = current_user.profit_overall_btc,
                                profit_overall_usd = current_user.profit_overall_usd,
                                sharpe_ratio=current_user.sharpe_ratio,
                                deviation=current_user.deviation,
                                sortino_ratio=current_user.sortino_ratio,
                                current_user=current_user,
                                notifications=current_user.notifications.all(),
                                posts = Post.query.all(),
                           )

@app.route("/api/v1/user_stats/",methods=['GET','POST'])
@login_required
def user_info():
    # Initialize CCXT exchange object
    if 'exchange_name' in request.json:
        exchange_name = request.json['exchange_name']
    else :
        exchange_name = None

    if 'user_id' in request.json:
        user_id = request.json['user_id']
        current_user2 = User.query.filter(User.id==user_id).first()
    else:
        current_user2 = current_user
    
    if exchange_name:
        exchange = connectExchange(exchange_name)
        # Retrieve historical price data for BTC/USDT and ETH/USDT

        open_orders = exchange.fetch_open_orders()
        transactions = exchange.fetch_ledger()
    else:
        open_orders = []
        transactions = []

    for exchange_user in current_user2.exchanges:
        api_key,api_secret,password = exchange_user.get_creds()
        if password:
                exchangeNow = getattr(ccxt, exchange_user.name)({
                    'apiKey': api_key,
                    'secret': api_secret,
                    'password':password,
                })
        else:
            exchangeNow = getattr(ccxt, exchange_user.name)({
                'apiKey': api_key,
                'secret': api_secret,
            })
        if exchange_user.demo:
            exchangeNow.set_sandbox_mode(True)

        for trans in exchangeNow.fetch_ledger():
            trans['exchange'] = exchange_user.name
            transactions.append(trans)

    return jsonify({
                        'exchnages':[exchange.serialize() for exchange in current_user2.exchanges.all()],
                        'open_orders':open_orders,
                        'transactions':transactions,
                        'balance_usd':current_user2.balance_usd,
                        'balance_btc':current_user2.balance_btc,
                        'profit_monthly_btc':current_user2.profit_monthly_btc,
                        'profit_monthly_usd':current_user2.profit_monthly_usd,
                        'profit_daily_btc':current_user2.profit_daily_btc,
                        'profit_daily_usd':current_user2.profit_daily_usd,
                        'profit_monthly_percent_btc':current_user2.profit_monthly_percent_btc,
                        'profit_monthly_percent_usd':current_user2.profit_monthly_percent_usd,
                        'profit_daily_percent_btc':current_user2.profit_daily_percent_btc,
                        'profit_daily_percent_usd':current_user2.profit_daily_percent_usd,
                        'profit_overall_btc':current_user2.profit_overall_btc,
                        'profit_overall_usd':current_user2.profit_overall_usd,
                        'sharpe_ratio':current_user2.sharpe_ratio,
                        'sortino_ratio':current_user2.sortino_ratio,
                        'deviation':current_user2.deviation,
                    })

@app.route("/api/v1/edit_user_info/", methods=['POST'])
@login_required
def edit_user_info():
    current_user.img = request.data.decode("utf-8")
    db.session.commit()
    

@app.route("/api/v1/reset_stats")
@login_required
def reset_stats():
    current_user.reset_stats()
    return jsonify({"message":"your stats have been reset","ok":True})

@app.route("/api/v1/assets")
@login_required
def assets():
    exchange_name = request.args.get('exchange')
    
    assets_json = []
    if exchange_name.lower() != "all":
        exchange = connectExchange(exchange_name)
        assets = exchange.fetch_balance()
        for asset, amount in assets["total"].items():
            price = getPrice(exchange.name,asset+'/USDT')
            assets_json.append({"currency":asset,"free":assets["free"][asset],"used":assets["used"][asset],"total":amount,"price":price,'eqUSD':amount*price})
    else:
        for exchange_user in current_user.exchanges.all():
            api_key,api_secret,password = exchange_user.get_creds()
            if password:
                exchangeForUser = getattr(ccxt, exchange_user.name)({
                    'apiKey': api_key,
                    'secret': api_secret,
                    'password':password,
                })
            else:
                exchangeForUser = getattr(ccxt, exchange_user.name)({
                    'apiKey': api_key,
                    'secret': api_secret,
                })
            if exchange_user.demo:
                exchangeForUser.set_sandbox_mode(True)

            assets = exchangeForUser.fetch_balance()
            for asset, amount in assets["total"].items():
                price = getPrice(exchangeForUser.name,asset+'/USDT')
                if check_assets_json(assets_json, asset):
                    for asset_json in assets_json:
                        if asset_json['currency'] == asset:
                            asset_json['free'] += assets["free"][asset]
                            asset_json['used'] += assets["used"][asset]
                            asset_json['total'] += amount
                            asset_json['eqUSD'] += amount*price
                else:
                    assets_json.append({"currency":asset,"free":assets["free"][asset],"used":assets["used"][asset],"total":amount,"price":price,'eqUSD':amount*price})
    
    return jsonify(assets_json)

########################################################end of dashboard############################################################

@app.route("/subscription")
def pricing():
    return render_template("pricing.html",notifications = current_user.notifications.all(),exchanges=current_user.exchanges.all(),current_user=current_user,posts = Post.query.all())

#change subscription type
@app.route("/api/v1/subscription",methods=['POST'])
@login_required
def change_subscription():
    subscription_type = request.json['subscription_type']
    current_user.subType = subscription_type
    db.session.commit()
    return jsonify({'message':'subscription changed','ok':True})

@app.route("/api/v1/subscription",methods=['GET'])
@login_required
def get_subscription():
    return jsonify(current_user.subType)

#knowledge base
@app.route("/knowledge_base",methods=['GET','POST'])
def kb():
    if request.method == 'POST':
        return jsonify({'posts':Post.query.all(),'categories':Category.query.all()})
    else:
        return render_template("knowledge_base.html",
                                cats=Category.query.all(),
                                posts = Post.query.all(),
                                notifications=current_user.notifications.all(),
                                exchanges = current_user.exchanges.all(),
                            )

@app.route("/knowledge_base_cat/<category_id>",methods=['GET','POST'])
def kb_cat(category_id):
    if request.method == 'POST':
        return jsonify({'posts':Post.query.filter(Post.category_id==category_id).all(),'category':Category.query.filter(Category.id==category_id).first(),'articles':Post.query.filter(Post.category_id==category_id).all(),'ok':True,'message':'success'})
    else:
        return render_template("knowledge_base_cat.html",
                                articles=Post.query.filter(Post.category_id==category_id).all(),
                                category=Category.query.filter(Category.id==category_id).first(),
                                posts = Post.query.all(),
                                notifications=current_user.notifications.all(),
                                exchanges = current_user.exchanges.all(),
                            )

@app.route("/knowledge_base_post/<int:post_id>",methods=['GET','POST'])
def kb_post(post_id):
    if request.method == 'POST':
        return jsonify({'post':Post.query.filter(Post.id==post_id).first(),'posts':Post.query.all(),'ok':True,'message':'success'})
    else:
        return render_template("knowledge_base_post.html",
                                post=Post.query.filter(Post.id==post_id).first(),
                                posts = Post.query.all(),
                                notifications=current_user.notifications.all(),
                                exchanges = current_user.exchanges.all(),
                            )


@app.route('/user/profile')
@login_required
def user_profile():
    return render_template('user-profile.html',exchanges=current_user.exchanges.all(),current_user=current_user,notifications=current_user.notifications.all(),posts = Post.query.all())

@app.route('/user/setting')
@login_required
def user_privacy_setting():
    return render_template('user-privacy-setting.html',exchanges=current_user.exchanges.all(),current_user=current_user,notifications=current_user.notifications.all(),posts = Post.query.all())


@app.route("/getData/")
def search2():
    symbols = search()
    #symbols2 = [symbol['symbol'][:symbol['symbol'].index(symbol['currency_code'])] + '/' + symbol['currency_code'] for symbol in symbols if symbol['currency_code'] == 'USDT' and '.P' not in symbol['symbol']]
    return jsonify(symbols)

@app.route('/api/v1/order_book_history')
def order_book_history():
    exchange = request.args.get("exchange")
    market = request.args.get("market")
    pair = request.args.get("pair")
    order_book = getattr(ccxt, exchange)().fetch_order_book(symbol=pair+"/"+market,limit=1)
    if order_book:
        socketio.emit('last_order', json.dumps(order_book))
    return "true"

@app.route('/api/v1/last_trades_history')
def last_trades_history():
    exchange = request.args.get("exchange")
    market = request.args.get("market")
    pair = request.args.get("pair")
    last_trades = getattr(ccxt, exchange)().fetch_trades(symbol=pair+"/"+market,limit=1)[0]
    if last_trades:
        socketio.emit('last_trade', json.dumps(last_trades))
    return "true"

@app.route('/api/v1/live_balance')
def live_balance():
    exchange = request.args.get("exchange")
    symbol = request.args.get("symbol")
    exchange = connectExchange(exchange)
    try:
        balance = exchange.fetch_balance()[symbol]['free']
        #socketio.emit('live_balance', json.dumps(balance))
    except:
        balance = 0
        #socketio.emit('live_balance',json.dumps([current_user.id,balance]))
    return jsonify(balance)

@app.route('/api/v1/live_price')
def live_price():
    exchange = request.args.get("exchange").upper().replace("OKEX",'OKX')
    market = request.args.get("market")
    pair = request.args.get("pair")
    stream = request.args.get("stream")

    if stream is None:
        stream = "true"

    try:
        if pair+"/"+market == 'USDT/USDT':
            return jsonify(1)
  
        if market == 'USDT':
            symbol_id = f"{str(exchange).upper().replace('OKEX','OKX')}{pair+market}"
            with open("pricesData/"+f"{symbol_id}.json", "r") as f:
                price = json.load(f)[pair+'/'+market][0]
        else:
            price1 = 0
            price2 = 0
            symbol_id1 = f"{str(exchange).upper().replace('OKEX','OKX')}{pair+'USDT'}"
            with open("pricesData/"+f"{symbol_id1}.json", "r") as f:
                price1 = json.load(f)[pair+"/"+'USDT'][0]
            symbol_id2 = f"{str(exchange).upper().replace('OKEX','OKX')}{market+'USDT'}"
            with open("pricesData/"+f"{symbol_id2}.json", "r") as f:
                price2 = json.load(f)[market+"/"+'USDT'][0]
            if  price1 == 0:
                price = 0
            else:
                price = price2/price1
    except FileNotFoundError:
        price = 0

    if price and stream == "true":
        socketio.emit('live_price', json.dumps([current_user.id,price]))
    return jsonify(price)

@app.route('/api/v1/live_crypto_data')
def live_crypto_data():
    exchange = request.args.get("exchange").upper().replace("OKEX",'OKX')
    market = request.args.get("market")
    pair = request.args.get("pair")

    try:
        if pair+"/"+market == 'USDT/USDT':
            return jsonify(1)
  
        if market == 'USDT':
            symbol_id = f"{str(exchange).upper().replace('OKEX','OKX')}{pair+market}"
            with open("volumesData/"+f"{symbol_id}.json", "r") as f:
                data = json.load(f)[pair+'/'+market]
        else:
            price1 = 0
            price2 = 0
            symbol_id1 = f"{str(exchange).upper().replace('OKEX','OKX')}{pair+'USDT'}"
            with open("volumesData/"+f"{symbol_id1}.json", "r") as f:
                data1 = json.load(f)[pair+"/"+'USDT']
            symbol_id2 = f"{str(exchange).upper().replace('OKEX','OKX')}{market+'USDT'}"
            with open("volumesData/"+f"{symbol_id2}.json", "r") as f:
                data2 = json.load(f)[market+"/"+'USDT']
            if  price1 == 0:
                price = 0
            else:
                price = price2/price1
            data = [data1[0]/data[1] for data in zip(data1,data2)]
    except FileNotFoundError:
        data = {}
        
    return jsonify({'data':data,'price':getPrice(exchange,pair+"/"+market)})

@app.route('/api/v1/indicators')
def indicators():
    exchange = request.args.get("exchange")
    market = request.args.get("market")
    pair = request.args.get("pair")
    interval = request.args.get("interval")
    indicators = update_symbol_data(pair+'/'+market,interval,exchange)
    socketio.emit('indicators', json.dumps(indicators))
    return "true"

                 
###############################################################################################################
      

@app.route('/api/v1/indicators_signals', methods=['GET'])
@login_required
def indicators_signals():
    interval = request.args.get("interval")
    exchange_name = request.args.get("exchange")

    exchange = connectExchange(exchange_name)

    pairs = []
    for currency in exchange.fetch_markets():
        if currency['active'] and currency['spot']:
            pairs.append(currency['symbol'])

    return calculate_signals(pairs,interval,exchange_name)

##########################################################################################

def check_assets_json(assets_json, currency):
  """
  Check if the array of assets_json contains json fiel which currency has teh assets value.

  Args:
    assets_json: The array of assets_json.
    currency: The currency to check.

  Returns:
    True if the array of assets_json contains json fiel which currency has teh assets value, False otherwise.
  """

  for asset in assets_json:
    if asset["currency"] == currency:
      return True
  return False

#####################################User_settings###################################

@app.route('/api/v1/user_settings/ip_check', methods=['POST'])
@login_required
def user_settings_ip_check():
    isActive = request.json['isActive']
    current_user.ip_check = isActive
    db.session.commit()

#####################################admin###################################

@app.route('/api/admin/v1/send_custom_notification', methods=['POST'])
@login_required
def send_custom_notification():
    message = request.json['message']
    user_id = request.json['user_id']
    send_notification(message+"***system",user_id)
    return jsonify({"message": "the message has been sent successfully",'ok':True})