from flask import render_template, request, redirect, url_for, jsonify,Response
import ccxt
from flask_login import login_required,current_user
from crypto import app,db,celery
from crypto.models import User, Exchange, SmartTrade,Post
from crypto.notify import send_notification
from search_crypto import search
from crypto.exchanges import connectExchange
from time import sleep
from crypto.functions import getPrice

@app.route('/trade/')
@login_required
def trade():
    if current_user.exchanges.filter(Exchange.isActive==True).first() is None:
        return redirect(url_for('exchanges'))
    
    exchange = connectExchange()
    
    pairs = []
    for currency in exchange.fetch_markets():
        if currency['active'] and currency['spot']:
            pairs.append(currency['symbol'])

    return render_template('trade.html',
                                notifications=current_user.notifications.all(),
                                exchanges = current_user.exchanges.all(),
                                symbol=request.args.get('symbol'),
                                exchange=request.args.get('exchange'),
                                current_user=current_user,
                                pairs=pairs,
                                posts = Post.query.all()
                           )

@app.route('/api/v1/smart_trades/', methods=['GET'])
def get_smart_trades():
    # Retrieve all smart trades for the current user
    smart_trades = SmartTrade.query.filter_by(user_id=current_user.id).all()

    # Serialize the smart trades to JSON format
    serialized_smart_trades = [smart_trade.serialize() for smart_trade in smart_trades]

    # Return the serialized smart trades as a JSON response
    return jsonify(smart_trades=serialized_smart_trades)

@app.route('/api/v1/smart_trades/', methods=['POST'])
def create_smart_trade():
    # Retrieve the trade parameters from the request
    trade_type = str(request.json['trade_type'])
    symbol = request.json['symbol']
    price = float(request.json['price'])
    triggerPrice = float(request.json['triggerPrice'])
    buy_type = request.json['buy_type']
    total_amount = float(request.json['amount'])
    take_profits = request.json['take_profits']
    tpTriggerType = request.json['tpTriggerType']
    tpTriggerPxType = request.json['tpTriggerPxType']
    stop_loss = request.json['stop_loss']
    take_profit = request.json['take_profit']
    stop_loss_type = request.json['stop_loss_type']
    stop_loss_trigger_price = float(request.json['stop_loss_trigger_price'])
    stop_loss_price = float(request.json['stop_loss_price'])
    stop_loss_price_percent = float(request.json['stop_loss_price_percent'])
    trailing_take_profit = request.json['trailing_take_profit']
    trailing_stop_loss = request.json['trailing_stop_loss']
    trailing_deviation = float(request.json['trailing_deviation'])
    stop_loss_time_out = request.json['stop_loss_time_out']
    stop_loss_time_out_time = int(request.json['stop_loss_time_out_time'])
    exchange_name = request.json['exchange']
    deal_started = False

    # Create an instance of the desired exchange
    exchange = connectExchange(exchange_name)

    buy_trade = None
    buy_trade_id = None
    
    try:
        # Place a smart trade (buy and sell with once)
        if trade_type.lower() == "smart trade" or trade_type.lower() == "smart cover":
            if buy_type == 'limit':
                deal_started = True
                buy_trade = exchange.create_order(symbol, buy_type, 'buy', total_amount, price)
            elif buy_type == 'market':
                deal_started = True
                buy_trade = exchange.create_order(symbol, buy_type, 'buy', total_amount)
            '''elif buy_type == 'cond.limit':
                buy_trade = exchange.create_order(symbol, 'limit', 'buy', total_amount, price,params={
                    'triggerPrice': triggerPrice,
                })
            elif buy_type == 'cond.market':
                buy_trade = exchange.create_order(symbol, 'market', 'buy', total_amount,params={
                    'triggerPrice': triggerPrice,
                })'''
            if buy_type == 'limit' or buy_type == 'market':
                buy_price = exchange.fetch_order(buy_trade['id'],symbol)['price']
                buy_trade_id = buy_trade['id']
                send_notification(f'Smart Trade has completed a Quick buy on {exchange_name} for {symbol} with {buy_price} {symbol.split("/")[1]}***{buy_type} Smart Trade Buy Order')
            else:
                buy_price = price
            #current_user.append_to_open_orders([buy_trade['id'], symbol,'Smart trade buy'])
        else:
            buy_price = price
        
        sell_trades = []
        '''#take_profits 
        for take_profit in take_profits:
            print(take_profit)
            sell_price = take_profit[0] # Calculate sell price based on take profit
            sell_amount = take_profit[1]*total_amount/100
            if take_profit != take_profits[-1] or trailing_take_profit == False:
                if tpTriggerType == 'market':
                    sell_trade = exchange.create_order(symbol, 'market', 'sell', sell_amount,params={
                        'triggerPrice': sell_price,
                    })
                else:
                    sell_trade = exchange.create_order(symbol, 'limit', 'sell', sell_amount, sell_price,params={
                        'triggerPrice': sell_price,
                    })
                sell_trades.append(sell_trade)
                current_user.append_to_open_orders([sell_trade['id'], symbol,'Smart trade tp'])
                send_notification(f"the order with id {sell_trade['id']} has created***Smart Trade Take Profit")
        
        sell_trade_ids = [trade['id'] for trade in sell_trades]
        stop_loss_id = 0
        if trailing_stop_loss == False:
            if stop_loss_time_out == True:
                sleep(stop_loss_time_out_time)
            if stop_loss_type == 'limit':
                stop_loss_order = exchange.create_order(symbol, 'limit', 'sell', total_amount,stop_loss_price,params={
                    'triggerPrice': stop_loss_trigger_price,
                })
            else:
                stop_loss_order = exchange.create_order(symbol, 'market', 'sell', total_amount,params={
                    'triggerPrice': stop_loss_trigger_price,
                })

            current_user.append_to_open_orders([stop_loss_order['id'], symbol,'Stop loss'])
            send_notification(f"the order with id {stop_loss_order['id']} has created***Smart Trade Stop Loss")
            stop_loss_id = stop_loss_order['id']'''
        
        db.session.commit()
        print("***********************")
        # Create a new smart trade object with the parsed data
        smart_trade = SmartTrade(
            trade_type=trade_type,
            exchange=request.json['exchange'],
            base_currency=request.json['symbol'].split('/')[1],
            quote_currency=request.json['symbol'].split('/')[0],
            units=total_amount,
            amount=total_amount,
            user_id=current_user.id,
            buy_price=buy_price,
            buy_trigger_price=triggerPrice,
            stop_loss=stop_loss,
            take_profit=take_profit,
            take_profit_quantities=request.json['take_profits'],
            tpTriggerType=tpTriggerType,
            order_type=buy_type,
            #sell_order_ids=sell_trade_ids,
            buy_order_id=buy_trade_id,
            trailing_order_id=0,
            #stop_loss_id=stop_loss_id,
            #last_take_profit_id=sell_trade_ids[-1] if len(sell_trade_ids)!=0 else None,
            trailing_take_profit=trailing_take_profit,
            trailing_deviation=trailing_deviation,
            trailing_stop_loss=trailing_stop_loss,
            stop_loss_price_percent=stop_loss_price_percent,
            stop_loss_price=stop_loss_trigger_price,
            stop_loss_type=stop_loss_type,
            stop_loss_time_out=stop_loss_time_out,
            stop_loss_time_out_time=stop_loss_time_out_time,
            deal_started=deal_started
        )

        # Add the new smart trade to the database
        db.session.add(smart_trade)
        db.session.commit()

        #trailing_stop_loss
        #smart_trade_bot.delay(current_user.id,smart_trade.id)

        return jsonify({'message':f"Smart Trade executed successfully.",'ok':True})

    except Exception as e:
        return jsonify({'message':f"Error executing Smart Trade: {e}"})

@app.route('/api/v1/smart_trades/edit/<int:smart_trade_id>', methods=['POST'])
def edit_smart_trade(smart_trade_id):
    # Get the smart trade from the database
    smart_trade = SmartTrade.query.get(smart_trade_id)

    # Retrieve the trade parameters from the request
    trade_type = str(request.json['trade_type'])
    symbol = request.json['symbol']
    price = float(request.json['price'])
    triggerPrice = float(request.json['triggerPrice'])
    buy_type = request.json['buy_type']
    total_amount = float(request.json['amount'])
    stop_loss = request.json['stop_loss']
    take_profit = request.json['take_profit']
    tpTriggerType = request.json['tpTriggerType']
    stop_loss_type = request.json['stop_loss_type']
    stop_loss_trigger_price = float(request.json['stop_loss_trigger_price'])
    stop_loss_price_percent = float(request.json['stop_loss_price_percent'])
    trailing_take_profit = request.json['trailing_take_profit']
    trailing_stop_loss = request.json['trailing_stop_loss']
    trailing_deviation = float(request.json['trailing_deviation'])
    stop_loss_time_out = request.json['stop_loss_time_out']
    stop_loss_time_out_time = int(request.json['stop_loss_time_out_time'])
    exchange_name = request.json['exchange']

    # Check if the smart trade exists
    if not smart_trade:
        return jsonify({'message': 'Smart trade not found'})

    # Get the exchange from the smart trade
    exchange = connectExchange(exchange_name)

    # Cancel the smart trade on the exchange
    try:
        if smart_trade.buy_order_id:
            if exchange.fetch_order(smart_trade.buy_order_id,symbol=smart_trade.quote_currency+'/'+smart_trade.base_currency)['status'] == 'open':
                exchange.cancel_order(smart_trade.buy_order_id, symbol=smart_trade.quote_currency+'/'+smart_trade.base_currency)
                smart_trade.deal_started=False
                smart_trade.units=total_amount
                smart_trade.amount=total_amount
                smart_trade.buy_price=price
                smart_trade.buy_trigger_price=triggerPrice
                smart_trade.order_type=buy_type
                
        smart_trade.trade_type=trade_type
        #smart_trade.exchange=request.json['exchange']
        smart_trade.take_profit_quantities=request.json['take_profits']
        smart_trade.tpTriggerType=tpTriggerType
        smart_trade.trailing_take_profit=trailing_take_profit
        smart_trade.stop_loss=request.json['stop_loss']
        smart_trade.trailing_stop_loss=trailing_stop_loss
        smart_trade.stop_loss_price_percent=stop_loss_price_percent
        smart_trade.stop_loss_price=stop_loss_trigger_price
        smart_trade.stop_loss_type=stop_loss_type
        smart_trade.stop_loss_time_out=stop_loss_time_out
        smart_trade.stop_loss_time_out_time=stop_loss_time_out_time
        smart_trade.stop_loss=stop_loss
        smart_trade.take_profit=take_profit
        smart_trade.trailing_deviation = trailing_deviation
        db.session.commit()

        return jsonify({'message': 'Smart trade edited successfully','ok':True})

    except Exception as e:
        return jsonify({'message': f'Error editing smart trade: {e}'})
    

@app.route('/api/v1/smart_trades/open/<int:smart_trade_id>', methods=['POST'])
def open_smart_trade(smart_trade_id):
    # Get the smart trade from the database
    smart_trade = SmartTrade.query.get(smart_trade_id)

    # Check if the smart trade exists
    if not smart_trade:
        return jsonify({'message': 'Smart trade not found'})

    # Get the exchange from the smart trade
    exchange = connectExchange()

    # Cancel the smart trade on the exchange
    try:
        smart_trade.isActive = True
        db.session.commit()
        return jsonify({'message': 'Smart trade opened successfully','ok':True})

    except Exception as e:
        return jsonify({'message': f'Error opening smart trade: {e}'})

@app.route('/api/v1/smart_trades/close/<int:smart_trade_id>', methods=['POST'])
def close_smart_trade(smart_trade_id):
    # Get the smart trade from the database
    smart_trade = SmartTrade.query.get(smart_trade_id)

    # Check if the smart trade exists
    if not smart_trade:
        return jsonify({'message': 'Smart trade not found'})

    # Get the exchange from the smart trade
    exchange = connectExchange()

    # Cancel the smart trade on the exchange
    try:
        smart_trade.isActive = False
        db.session.commit()
        return jsonify({'message': 'Smart trade closed successfully','ok':True})

    except Exception as e:
        return jsonify({'message': f'Error closing smart trade: {e}'})

@app.route('/api/v1/smart_trades/cancel/<int:smart_trade_id>', methods=['POST'])
def cancel_smart_trade(smart_trade_id):
    # Get the smart trade from the database
    smart_trade = SmartTrade.query.get(smart_trade_id)

    # Check if the smart trade exists
    if not smart_trade:
        return jsonify({'message': 'Smart trade not found'})

    # Get the exchange from the smart trade
    exchange = connectExchange()

    # Cancel the smart trade on the exchange
    try:
        if smart_trade.buy_order_id:
            if exchange.fetch_order(smart_trade.buy_order_id,symbol=smart_trade.quote_currency+'/'+smart_trade.base_currency)['status'] == 'open':
                exchange.cancel_order(smart_trade.buy_order_id, symbol=smart_trade.quote_currency+'/'+smart_trade.base_currency)
        db.session.delete(smart_trade)
        db.session.commit()
        return jsonify({'message': 'Smart trade cancelled successfully','ok':True})

    except Exception as e:
        return jsonify({'message': f'Error cancelling smart trade: {e}'})

# GET /api/v1/smart_trades/:id
@app.route('/api/v1/smart_trades/<int:id>', methods=['GET'])
def get_smart_trade(id):
    # Retrieve the smart trade with the specified ID and user ID
    smart_trade = SmartTrade.query.filter_by(id=id, user_id=current_user.id).first()

    # If the smart trade does not exist, return a 404 error response
    if not smart_trade:
        return jsonify({'error': f'Smart trade with ID {id} does not exist or does not belong to this user'}), 404

    # Serialize the smart trade to JSON format
    serialized_smart_trade = smart_trade.serialize()

    # Return the serialized smart trade as a JSON response
    return jsonify(smart_trade=serialized_smart_trade)

# PUT /api/v1/smart_trades/:id
@app.route('/api/v1/smart_trades/<int:id>', methods=['PUT'])
def update_smart_trade(id):
    # Retrieve the smart trade with the specified ID and user ID
    smart_trade = SmartTrade.query.filter_by(id=id, user_id=current_user.id).first()

    # If the smart trade does not exist, return a 404 error response
    if not smart_trade:
        return jsonify({'error': f'Smart trade with ID {id} does not exist or does not belong to this user'}), 404

    # Parse the request body to get the updated smart trade data
    data = request.json

    # Update the smart trade object with the parsed data
    smart_trade.name = data.get('name', smart_trade.name)
    smart_trade.strategy = data.get('strategy', smart_trade.strategy)
    smart_trade.exchange = data.get('exchange', smart_trade.exchange)
    smart_trade.base_currency = data.get('base_currency', smart_trade.base_currency)
    smart_trade.quote_currency = data.get('quote_currency', smart_trade.quote_currency)
    smart_trade.allocation = data.get('allocation', smart_trade.allocation)
    smart_trade.conditions = data.get('conditions', smart_trade.conditions)

    # Commit the changes to the database
    db.session.commit()

    # Serialize the updated smart trade to JSON format
    serialized_smart_trade = smart_trade.serialize()

    # Return the serialized smart trade as a JSON response
    return jsonify(smart_trade=serialized_smart_trade)


# DELETE /api/v1/smart_trades/:id
@app.route('/api/v1/smart_trades/<int:id>', methods=['DELETE'])
def delete_smart_trade(id):
    # Retrieve the smart trade with the specified ID and user ID
    smart_trade = SmartTrade.query.filter_by(id=id, user_id=current_user.id).first()

    # If the smart trade does not exist, return a 404 error response
    if not smart_trade:
        return jsonify({'error': f'Smart trade with ID {id} does not exist or does not belong to this user'}), 404

    # Delete the smart trade from the database
    db.session.delete(smart_trade)
    db.session.commit()

    # Return a success message as a JSON response
    return jsonify({'message': f'Smart trade with ID {id} has been deleted'})

@celery.task
def smart_trade_bot_all():
    with app.app_context(): 
        while True:
            sleep(2)
            smart_trade_bots = SmartTrade.query.all()
            for smart_trade_bot in smart_trade_bots:
                try:
                    current_user = User.query.filter_by(id=smart_trade_bot.user_id).first()
                    smart_trade_bot = SmartTrade.query.filter_by(id=smart_trade_bot.id).first()
                    if smart_trade_bot.isActive and smart_trade_bot and smart_trade_bot.units > 0:
                        symbol = smart_trade_bot.quote_currency+'/'+smart_trade_bot.base_currency
                        exchange_name = smart_trade_bot.exchange

                        if smart_trade_bot.units == 0:
                            smart_trade_bot.isActive = False
                            db.session.commit()

                        price = getPrice(exchange_name, symbol)
                        smart_trade_bot.last_price = price

                        print("-----------------------------------------------------------")
                        print("Smart Trade Bot")
                        print("-----------------------------------------------------------")

                        db.session.commit()
                        api_key,api_secret,password = current_user.exchanges.filter(Exchange.name == exchange_name).first().get_creds()
                        if password:
                            exchange = getattr(ccxt, exchange_name)({
                                'apiKey': api_key,
                                'secret': api_secret,
                                'password': password,
                            })
                        else:
                            exchange = getattr(ccxt, exchange_name)({
                                'apiKey': api_key,
                                'secret': api_secret,
                            })

                        if current_user.exchanges.filter(Exchange.name == exchange_name).first().demo:
                            exchange.set_sandbox_mode(True)

                        #conditional buy orders
                        if smart_trade_bot.trade_type.lower() == "smart trade" or smart_trade_bot.trade_type.lower() == "smart cover": 
                            if price >= smart_trade_bot.buy_trigger_price and smart_trade_bot.deal_started == False:
                                smart_trade_bot.deal_started = True
                                if smart_trade_bot.order_type == 'cond.limit':
                                    buy_trade = exchange.create_order(symbol, 'limit', 'buy', smart_trade_bot.amount, smart_trade_bot.buy_price)
                                elif smart_trade_bot.order_type == 'cond.market':
                                    buy_trade = exchange.create_order(symbol, 'market', 'buy', smart_trade_bot.amount)
                                smart_trade_bot.buy_order_id = buy_trade['id']
                                send_notification(f'Smart Trade has started a Condtional Quick buy on {exchange_name} for {symbol} with {exchange.fetch_order(buy_trade["id"],symbol=symbol)["price"]} {smart_trade_bot.base_currency}***{smart_trade_bot.order_type}Smart Trade Buy Order', current_user.id,smart_trade_bot.exchange)
                                db.session.commit()
                            

                        #take-profit-orders
                        if smart_trade_bot.take_profit:
                            for take_profit in smart_trade_bot.take_profit_quantities:
                                sell_price = take_profit[0] # Calculate sell price based on take profit
                                sell_amount = take_profit[1]*smart_trade_bot.amount/100
                                if price >= sell_price if (smart_trade_bot.trade_type.lower() != "smart cover" and smart_trade_bot.trade_type.lower() != "smart buy") else price <= sell_price:
                                    if take_profit == smart_trade_bot.take_profit_quantities[-1]:
                                        smart_trade_bot.last_take_profit = True
                                    if take_profit != smart_trade_bot.take_profit_quantities[-1] or smart_trade_bot.trailing_take_profit == False:
                                        if smart_trade_bot.tpTriggerType == 'market':
                                            sell_trade = exchange.create_order(symbol, 'market', 'sell', sell_amount)
                                        else:
                                            sell_trade = exchange.create_order(symbol, 'limit', 'sell', sell_amount, sell_price)
                                        #smart_trade_bot.sell_order_ids.append(sell_trade['id'])
                                        smart_trade_bot.units = smart_trade_bot.units - sell_amount
                                        db.session.commit()
                                        send_notification(f'Smart Trade has completed a Take Profit on {exchange_name} for {symbol} with {sell_price} {smart_trade_bot.base_currency}***Take Profit Sell Order', current_user.id,smart_trade_bot.exchange)
                                    db.session.commit()

                        # Check if any take profit has been executed
                        '''for sell_order_id in smart_trade_bot.sell_order_ids:
                            try:
                                if exchange.fetch_order(int(sell_order_id), smart_trade_bot.quote_currency+'/'+smart_trade_bot.base_currency):
                                    if exchange.fetch_order(int(sell_order_id), smart_trade_bot.quote_currency+'/'+smart_trade_bot.base_currency).get('status') == "closed":
                                        smart_trade_bot.sell_order_ids.remove(sell_order_id)
                                        filled_amount = exchange.fetch_order(sell_order_id, smart_trade_bot.quote_currency+'/'+smart_trade_bot.base_currency)['filled']
                                        print("Take profit executed. Filled amount:", filled_amount)
                                        smart_trade_bot.units = filled_amount
                                        if sell_order_id == smart_trade_bot.sell_order_ids[-1]:
                                            smart_trade_bot.last_take_profit = True
                                        db.session.commit()
                            except Exception as e:
                                print(e)
                                pass'''

                        ######trailing_stop_loss
                        
                        smart_trade_bot.last_price = price
                        if price > smart_trade_bot.last_price:
                            # Update stop loss price
                            if smart_trade_bot.trailing_stop_loss:
                                smart_trade_bot.stop_loss_price = price + price * float(smart_trade_bot.stop_loss_price_percent)/100
                            if smart_trade_bot.trailing_take_profit and smart_trade_bot.last_take_profit:
                                smart_trade_bot.stop_loss_price = price + price * float(smart_trade_bot.trailing_deviation)/100
                        db.session.commit()

                        print("Remaining units:", smart_trade_bot.units)
                        if (price <= smart_trade_bot.stop_loss_price if (smart_trade_bot.trade_type.lower() != "smart cover" and smart_trade_bot.trade_type.lower() != "smart buy") else price >= smart_trade_bot.stop_loss_price) and smart_trade_bot.units > 0 and smart_trade_bot.deal_started and smart_trade_bot.stop_loss:
                            # Making the stop loss sell order
                            if smart_trade_bot.stop_loss_time_out:
                                sleep(smart_trade_bot.stop_loss_time_out_time)
                            trailing_order = exchange.create_order(symbol, 'market', 'sell', smart_trade_bot.units)
                            smart_trade_bot.units = 0
                            smart_trade_bot.isActive = False
                            db.session.commit()

                            # Send notification
                            message = f"Stop loss sell order executed for {symbol} on {smart_trade_bot.exchange} by {price} {smart_trade_bot.base_currency}***Smart Trade"
                            send_notification(message, current_user.id,smart_trade_bot.exchange)
                    else:
                        continue
                except Exception as e:
                    print(e)
                    continue