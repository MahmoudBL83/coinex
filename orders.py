import json
from flask import render_template, request, redirect, url_for, jsonify,Response
import ccxt
from flask_login import login_required,current_user
from crypto import app
from crypto.models import Exchange,Post
from crypto.notify import send_notification
from crypto.exchanges import connectExchange

@app.route('/api/v1/order/', methods=['POST'])
@login_required
def place_order():
    '''
    This function is used to place an order on the exchange.
    Params:
        symbol: the symbol of the order
        type: the type of the order (limit or market)
        order_price: the price of the order
        trigger_price: the trigger price for conditional orders
        amount: the amount of the order
        side: the side of the order (buy or sell)
    '''
    exchange_name = current_user.exchanges.filter(Exchange.isActive==True).first().name
    
    # Instantiate the exchange API client using the provided API credentials
    exchange = connectExchange(exchange_name)
    
    try:
        # Parse the order parameters from the request body
        symbol = str(request.json['symbol']).upper()
        order_type = str(request.json['type']).lower()
        if request.json['order_price']:
            order_price = float(request.json['order_price'])
        else:
            order_price = 0
        amount = float(request.json['amount'])
        side = str(request.json['side']).lower()

        # Place the order on the exchange and return the order details as a JSON object
        if order_type == 'limit':
            buy_trade = exchange.create_order(symbol, order_type, side, amount, order_price)
            send_notification(f'Quick buy Finished on {exchange_name} for {symbol} with {order_price} {symbol.split("/")[1]} ***Limit Buy Order')
        elif order_type == 'market':
            buy_trade = exchange.create_order(symbol, order_type, side, amount)
            buy_trade_price = exchange.fetch_order(buy_trade["id"], symbol=symbol)["price"]
            send_notification(f'Quick {side} finished on {exchange_name} for {symbol} with {buy_trade_price} {symbol.split("/")[1]} ***Market {side} Order')
        elif order_type == 'cond.limit':
            buy_trade = exchange.create_order(symbol, 'limit', side, amount, order_price, params={
                'triggerPrice': float(request.json['trigger_price']),
            })
            send_notification(f'Conditional Quick {side} started on {exchange_name} for {symbol} with {float(request.json["trigger_price"])} {symbol.split("/")[1]} ***Conditional Limit {side} Order')
        elif order_type == 'cond.market':
            buy_trade = exchange.create_order(symbol, 'market', side, amount, params={
                'triggerPrice': float(request.json['trigger_price']),
            })
            send_notification(f'Conditional Quick {side} started on {exchange_name} for {symbol} with {float(request.json["trigger_price"])} {symbol.split("/")[1]} ***Conditional Market {side} Order')
            
        return jsonify({'message': 'The operation was successful', 'ok': True, 'order': buy_trade})
    
    except ccxt.InvalidOrder as e:
        return jsonify({'message': str(e), 'ok': False})
    
    except ccxt.DDoSProtection as e:
        return jsonify({'message': 'DDoS protection error: ' + str(e), 'ok': False})
    
    except ccxt.ExchangeError as e:
        return jsonify({'message': 'Exchange error: ' + str(e), 'ok': False})
    
    except ccxt.AuthenticationError as e:
        return jsonify({'message': 'Authentication error: ' + str(e), 'ok': False})
    
    except ccxt.NetworkError as e:
        return jsonify({'message': 'Network error: ' + str(e), 'ok': False})
    
    except Exception as e:
        return jsonify({'message': 'An error occurred: ' + str(e), 'ok': False})

@app.route('/api/v1/order/cancel',methods=['POST'])
@login_required
def cancel_order():
    '''
    this function is used to cancel an order on the exchange
    params:
        id: the id of the order
        symbol: the symbol of the order
    '''
    id = request.json['id']
    exchange_name = current_user.exchanges.filter(Exchange.isActive==True).first().name
    symbol = request.json['symbol']
    exchange = connectExchange(exchange_name)
    try:
        order = exchange.cancel_order(id,symbol=symbol)
        return jsonify({'message': f'the order with id {id} has been cancelled','ok':True,'order': order})
    except ccxt.InvalidOrder:
        return jsonify({'message': 'the canel operation failed','ok':False})

#############################################---------------HISTORY-START-------------#############################################

@app.route('/api/v1/history/open_orders/', methods=['GET','POST'])
@login_required
def history_open_orders():
    # Instantiate the exchange API client using the provided API credentials
    if current_user.exchanges.filter(Exchange.isActive==True).first() is None:
        #return jsonify('message','No active exchange found')
        return redirect(url_for('exchanges'))
    exchange_name = current_user.exchanges.filter(Exchange.isActive==True).first().name
    exchange = connectExchange(exchange_name)
    open_orders = exchange.fetch_open_orders()
    
    page = int(request.args.get('page', 1))  # Get the current page number from the request query parameters
    items_per_page = 20  # Number of items to display per page
    start_index = (page - 1) * items_per_page
    end_index = start_index + items_per_page
    formatted_history = []
    for order in open_orders:
        formatted_open_order = {
            'id': order['id'],
            'symbol': order['symbol'],
            'filled_amount': order['filled'],
            'order_type': order['type'],
            'total_amount': order['amount'],
            'remaining_amount': order['remaining'],
            'cost': order['cost'],
            'trigger_price': str(order['triggerPrice']) + "" + order['symbol'].split("/")[1] if order['triggerPrice']  else "--",
            'order_price': str(order['price']) + " " + order['symbol'].split("/")[1] if order['price'] else "market",
            'side': order['side'],
            #'tp': order['takeProfitPrice'],
            #'sl': order['stopLossPrice'],
            'status': order['status'],
            'time': order['timestamp'],
            'reduceOnly': order['reduceOnly'],
            #'instrument': order['info']['instId'],
            #'instType': order['info']['instType'],
        }
        formatted_history.append(formatted_open_order)
    paginated_history = formatted_history[start_index:end_index]
    if request.method == 'POST':
        formatted_history_json = json.dumps(paginated_history, indent=4)
        return Response(formatted_history_json, content_type='application/json')
    else:
        total_pages = (len(open_orders) + items_per_page - 1) // items_per_page
        print(open_orders)
        return render_template("history_open_orders.html",notifications=current_user.notifications.all(),exchanges=current_user.exchanges.all(), orders=paginated_history, total_pages=total_pages, current_page=page,current_user=current_user,posts = Post.query.all()) 

@app.route('/api/v1/history/orders/', methods=['GET','POST'])
@login_required
def history_orders():
    if current_user.exchanges.filter(Exchange.isActive==True).first() is None:
        return redirect(url_for('exchanges'))
    exchange_name = current_user.exchanges.filter(Exchange.isActive==True).first().name
    exchange = connectExchange(exchange_name)

    history_orders = exchange.fetch_closed_orders()[::-1]
    print(history_orders)
    # Pagination parameters
    page = int(request.args.get('page', 1))  # Get the current page number from the request query parameters
    items_per_page = 20  # Number of items to display per page
    start_index = (page - 1) * items_per_page
    end_index = start_index + items_per_page
    formatted_history = []

    for order in history_orders:
        formatted_order = {
            'id': order['id'],
            'timestamp': order['timestamp'],
            'datetime': order['datetime'],
            'side': order['side'],
            'order_type': order['type'],
            #'fillPx': order['info']['fillPx'],
            #'px': order['info']['px'] if order['info']['px'] else "market",
            #'fillSz': order['info']['fillSz'],
            #'sz': order['info']['sz'],
            'reduceOnly': order['reduceOnly'],
            #'remaining': order['remaining'],
            'stopLossPrice': order['stopLossPrice'],
            'stopPrice': order['stopPrice'],
            'takeProfitPrice': order['takeProfitPrice'],
            'trigger_price': str(order['triggerPrice'])+ " " + order['symbol'].split("/")[1] if order['triggerPrice'] else "--",
            'order_price': str(order['price'])+ " " + order['symbol'].split("/")[1] if order['price'] else "market",
            'status': order['status'],
            'symbol': order['symbol'],
            'amount': abs(order['amount'] or 0),
            #'average': order['average'],
            #'cost': order['cost'],
            'fee': str(order['fee']['cost']) + " " + order["fee"]["currency"] if order['fee'] else 0,
            #'currency1': order['symbol'].split('/')[0],
            #'currency2':order['symbol'].split('/')[1],
            #'filled':order['filled'],
            #'filled_cost':order['cost'],
        }
        formatted_history.append(formatted_order)

    paginated_history = formatted_history[start_index:end_index]
    if request.method == 'POST':
        formatted_history_json = json.dumps(paginated_history, indent=4)
        return Response(formatted_history_json, content_type='application/json')
    else:
        total_pages = (len(history_orders) + items_per_page - 1) // items_per_page
        return render_template("history_orders.html",
                                    exchanges=current_user.exchanges.all(),
                                    notifications=current_user.notifications.all(), 
                                    orders=paginated_history, total_pages=total_pages,
                                    current_page=page,
                                    current_user=current_user,
                                    posts = Post.query.all()
                                 )  

@app.route('/api/v1/history/trades/', methods=['GET', 'POST'])
@login_required
def history_trades_history():
    if current_user.exchanges.filter(Exchange.isActive==True).first() is None:
        return redirect(url_for('exchanges'))
    exchange_name = current_user.exchanges.filter(Exchange.isActive==True).first().name
    exchange = connectExchange(exchange_name)

    if exchange.has['fetchLedger']:
        trading_history = exchange.fetch_ledger()[::-1]
    else:
        trading_history = []

    # Pagination parameters
    page = int(request.args.get('page', 1))  # Get the current page number from the request query parameters
    items_per_page = 20  # Number of items to display per page
    start_index = (page - 1) * items_per_page
    end_index = start_index + items_per_page
    formatted_history = []
    for order in trading_history:
        formatted_order = {
            'id': order['id'],
            'timestamp': order['timestamp'],
            'order_type': order['type'],
            'side': 'Buy' if order['amount'] >= 0 else 'Sell',
            'currency': order['currency'],
            'symbol': order['symbol'],
            'amount': abs(order['amount']),
            'fee': order['fee']['cost'],
            'feeCcy':order['fee']['currency'],
        }
        formatted_history.append(formatted_order)
    paginated_history = formatted_history[start_index:end_index]
    print(trading_history[-1])
    if request.method == 'POST':
        formatted_history_json = json.dumps(paginated_history, indent=4)
        return Response(formatted_history_json, content_type='application/json')
    else:
        total_pages = (len(trading_history) + items_per_page - 1) // items_per_page
        return render_template("history_trading.html",
                                    exchanges=current_user.exchanges.all(),
                                    trading_history=paginated_history,
                                    total_pages=total_pages, 
                                    current_page=page,
                                    current_user=current_user,
                                    posts = Post.query.all(),
                                    notifications=current_user.notifications.all(),
                                )  

@app.route('/api/v1/history/positions_history/', methods=['GET', 'POST'])
@login_required
def history_positions_history():
    if current_user.exchanges.filter(Exchange.isActive==True).first() is None:
        return redirect(url_for('exchanges'))
    exchange_name = current_user.exchanges.filter(Exchange.isActive==True).first().name
    exchange = connectExchange(exchange_name)

    if exchange.has['fetchPositions']:
        positions_history = exchange.fetch_positions()[::-1]
        ()[::-1]
    else:
        positions_history = []

    # Pagination parameters
    page = int(request.args.get('page', 1))  # Get the current page number from the request query parameters
    items_per_page = 20  # Number of items to display per page
    start_index = (page - 1) * items_per_page
    end_index = start_index + items_per_page
    paginated_history = positions_history[start_index:end_index]
    print(positions_history)
    if request.method == 'POST':
        formatted_history_json = json.dumps(positions_history, indent=4)
        return Response(formatted_history_json, content_type='application/json')
    else:
        total_pages = (len(positions_history) + items_per_page - 1) // items_per_page
        return render_template("history_positions.html",exchanges=current_user.exchanges.all(), positions_history=paginated_history, total_pages=total_pages, current_page=page,current_user=current_user,posts = Post.query.all())  

@app.route('/api/v1/history/funding_history/', methods=['GET','POST'])
@login_required
def history_funding_history():
    if current_user.exchanges.filter(Exchange.isActive==True).first() is None:
        return redirect(url_for('exchanges'))
    exchange_name = current_user.exchanges.filter(Exchange.isActive==True).first().name
    exchange = connectExchange(exchange_name)

    transfers = exchange.fetch_transfers()[::-1]

    formatted_transfers = []
    for order in transfers:
        formatted_transfer = {
            'id': order['id'],
            'amount': round(float(order['amount']),4),
            'currency': order['currency'],
            'from': 'spot' if order['fromAccount']=='trading' else order['fromAccount'],
            'to': 'spot' if order['toAccount']=='trading' else order['toAccount'],
            'timestamp': order['timestamp'],
            'status': order['status'],
            #'type': 'Transfer out' if order['fromAccount']=='funding' else 'Transfer in',
        }
        if order['toAccount'] == 'funding' or order['fromAccount'] == 'funding' or True:
            formatted_transfers.append(formatted_transfer)

    if request.method == 'POST':
        return jsonify(transfers)
    else:
        return render_template("history_funding.html",
                                    exchanges=current_user.exchanges.all(),
                                    transfers=formatted_transfers,
                                    current_user=current_user,
                                    posts = Post.query.all(),
                                    notifications=current_user.notifications.all(),
                               )