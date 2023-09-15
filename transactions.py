from flask import render_template, request, redirect, url_for, jsonify,Response
import ccxt
from flask_login import login_required,current_user
from crypto import app
from crypto.models import User, Exchange, SmartTrade, Bot, SafetyOrder, Post, Category
from crypto.notify import send_notification
from crypto.exchanges import connectExchange

@app.route('/api/v1/deposit/', methods=['POST','GET'])
@login_required
def crypto_deposit():
    '''
        function for making deposit to exchange
        the parameters are:
        symbol: the symbol of the coin to deposit
        network: the network of the coin to deposit
        the response is:
        {
            "message": "successful deposit",
            "ok": true,
            "deposit": deposit
        }
        deposit is the response from the exchange
    '''
    if current_user.exchanges.filter(Exchange.isActive==True).first() is None:
        if request.method == 'POST':
            return jsonify('message','No active exchange found')
        else:
            return redirect(url_for('exchanges'))
        
    exchange_name = current_user.exchanges.filter(Exchange.isActive == True).first().name
    if request.method == 'POST':
        try:
            symbol = request.json['symbol']
            network = request.json['network']
            
            exchange = connectExchange(exchange_name)
            
            if exchange.fetch_currencies() is None or exchange.has['fetchDepositAddress']:
                return jsonify({'message': 'Depsoit is not possible'})
                
            # Initiate deposit with exchange
            deposit = exchange.fetch_deposit_address(symbol, {'network': network})
            print(deposit)
            return jsonify({'message':"successful deposit",'ok':True,'deposit':deposit})
        
        except ccxt.InsufficientFunds as e:
            return jsonify({'message': f'Error Depositing order on {exchange_name}: Insufficient funds. {str(e)}'})
        except ccxt.InvalidOrder as e:
            return jsonify({'message': f'Error Depositing order on {exchange_name}: Invalid order. {str(e)}'})
        except ccxt.NetworkError as e:
            return jsonify({'message': f'Error Depositing order on {exchange_name}: Network error. {str(e)}'})
        except ccxt.ExchangeError as e:
            return jsonify({'message': f'Error Depositing order on {exchange_name}: Exchange error. {str(e)}'})
        except ccxt.BaseError as e:
            return jsonify({'message': f'Error Depositing order on {exchange_name}: {str(e)}'})
        
    return render_template('deposit.html',
                            exchanges = current_user.exchanges.all(),
                            current_user=current_user,posts = Post.query.all(),
                            notifications=current_user.notifications.all(),
                            deposits = connectExchange().fetch_deposits(),
                        )

#get all deposits history
@app.route('/api/v1/deposits/', methods=['POST','GET'])
@login_required
def crypto_deposits():
    '''
    the deposits are returned in the following format:
    [
        {
            "info": {
                "currency": "BTC",
                "amount": "0.0001",
                "txid": "5f7a0a9c03aa675e4a06f5b0",
                "address": "3J98t1WpEZ73CNmQviecrnyiWrnqRhWNLy",
                "addressTo": "3J98t1WpEZ73CNmQviecrnyiWrnqRhWNLy",
                "type": "withdrawal",
                "timestamp": "1601817600000",
                "status": "success"
            },
        }
    ]
    '''
    return jsonify(connectExchange().fetch_deposits())

@app.route('/api/v1/transfer/', methods=['POST', 'GET'])
@login_required
def crypto_transfer():
    '''
        function for making transfer between spot and funding
        the parameters are:
        amount: the amount to transfer
        side: the side of the transfer (funding or spot)
        symbol: the symbol of the coin to transfer
    '''
    if current_user.exchanges.filter(Exchange.isActive==True).first() is None:
        if request.method == 'POST':
            return jsonify('message','No active exchange found')
        else:
            return redirect(url_for('exchanges'))
    exchange_name = current_user.exchanges.filter(Exchange.isActive == True).first().name
    exchange = connectExchange(exchange_name)
    if request.method == 'POST':
        amount = request.json['amount']
        side = request.json['side']
        symbol = request.json['symbol']

        try:
            if side == 'funding':
                result = exchange.transfer(symbol, amount,"spot", "funding")
                send_notification(f'Transfer completed on {exchange_name} for {amount} {symbol} from spot to funding***Transfer')
            else:
                result = exchange.transfer(symbol, amount, "funding","spot")
                send_notification(f'Transfer completed on {exchange_name} for {amount} {symbol} from funding to spot***Transfer')


            if result['id']:
                message = f'Transfer successful. ID: {result["id"]}'
                return jsonify({'message': message,'ok':True})
            else:
                return jsonify({'message': 'Transfer failed'})

        except ccxt.InsufficientFunds as e:
            return jsonify({'message': str(e)})

        except ccxt.ExchangeError as e:
            return jsonify({'message': str(e)})

        except ccxt.NetworkError as e:
            return jsonify({'message': str(e)})

        except Exception as e:
            return jsonify({'message': 'An error occurred. Please try again later.'})

    if exchange_name != 'bittrex' and exchange_name != 'coinbase':
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
            }
            if order['toAccount'] == 'funding' or order['fromAccount'] == 'funding' or True:
                formatted_transfers.append(formatted_transfer)

        return render_template('transfer.html',
                                    transfers = formatted_transfers,
                                    exchanges=current_user.exchanges.all(),
                                    current_user=current_user,
                                    posts = Post.query.all(),
                                    notifications=current_user.notifications.all()
                                )
    else:
        return render_template('404.html')

@app.route('/api/v1/convert/', methods=['POST','GET'])
@login_required
def crypto_convert():
    if current_user.exchanges.filter(Exchange.isActive==True).first() is None:
        if request.method == 'POST':
            return jsonify('message','No active exchange found')
        else:
            return redirect(url_for('exchanges'))
    exchange_name = current_user.exchanges.filter(Exchange.isActive == True).first().name
    
    if request.method == 'POST':
        # Extract the parameters from the JSON request
        amount = request.json['amount']
        order_type = request.json['order_type']
        source_asset = request.json['source_asset']
        target_asset = request.json['target_asset']

        try:
            # Create the exchange object with the API credentials
            exchange = connectExchange(exchange_name)
            # Construct the symbol based on the chosen assets
            symbol = f"{source_asset}/{target_asset}"
            
            # Check if the exchange supports the specified trading pair
            if exchange.has['createOrder']:
                # Set the order type based on the parameter
                if order_type == 'market':
                    order = exchange.create_order(symbol, 'market', 'sell', amount)
                    send_notification(f'Conversion completed on {exchange_name} to convert {amount} {source_asset} to {target_asset} for {order["price"]}***Convert')
                elif order_type == 'limit':
                    # Additional parameters for limit orders
                    price = request.json['price']
                    order = exchange.create_order(symbol, 'limit', 'sell', amount, price)
                    send_notification(f'Conversion started on {exchange_name} to convert {amount} {source_asset} to {target_asset} for {price}***Convert')
                    current_user.append_to_open_orders([order['id'], symbol,'convert'])
                else:
                    return jsonify({'message': 'Invalid order type. Supported types: market, limit.'})
                # Return the order details as JSON response
                return jsonify({'message': f"Conversion order created on {exchange_name}.",'ok':True, 'order': order})
            else:
                return jsonify({'message': f"{exchange_name} does not support the {symbol} trading pair."})

        except ccxt.ExchangeError as e:
            return jsonify({'message': str(e)})

        except ccxt.AuthenticationError as e:
            return jsonify({'message': 'Authentication failed. Check your API credentials.'})

        except ccxt.ExchangeNotAvailableError as e:
            return jsonify({'message': 'The exchange is currently not available.'})

        except Exception as e:
            return jsonify({'message': str(e)})
    
    return render_template('convert.html',exchanges = current_user.exchanges.all(),current_user=current_user,posts = Post.query.all(),notifications=current_user.notifications.all())


@app.route('/api/v1/withdraw/', methods=['POST','GET'])
@login_required
def crypto_withdraw():
    if current_user.exchanges.filter(Exchange.isActive==True).first() is None:
        if request.method == 'POST':
            return jsonify('message','No active exchange found')
        else:
            return redirect(url_for('exchanges'))
    exchange_name = current_user.exchanges.filter(Exchange.isActive == True).first().name
    if request.method == 'POST':
        try:
            amount = request.json['amount']
            recipient_address = request.json['recipient_address']
            currency = request.json['currency']
            network_user = request.json['network']
            exchange = connectExchange(exchange_name)

            if exchange.fetch_currencies() is None:
                return jsonify({'message': 'Withdraw is not possible'})

            # Specify the network parameter for each exchange
            params = {'network': network_user}
            # Add additional elif statements for other exchanges as needed

            # Execute the withdrawal and check the response for errors
            response = exchange.withdraw(currency, amount, recipient_address,None, params)
            if 'info' in response and 'status' in response['info'] and response['info']['status'] == '0':
                error_msg = "User identity verification is required for this withdrawal"
                return jsonify({"message": error_msg}), 400
            elif 'error' in response:
                error_msg = response['error']
                return jsonify({"message": error_msg}), 400
            else:
                # The response will contain information about the withdrawal, such as the ID of the withdrawal and its status
                print(response)
                return jsonify({"message": "withdraw done",'ok':True})
        except ccxt.NetworkError as e:
            # Handle network errors (e.g. connection issues)
            error_msg = f"Network error: {str(e)}"
            return jsonify({"message": error_msg}), 500
        except ccxt.ExchangeError as e:
            # Handle exchange errors (e.g. invalid parameters, insufficient funds)
            error_msg = f"Exchange error: {str(e)}"
            return jsonify({"message": error_msg}), 400
        except Exception as e:
            # Handle other errors (e.g. unexpected errors)
            error_msg = f"Unexpected error: {str(e)}"
            return jsonify({"message": error_msg}), 500
    
    if exchange_name != 'coinbase':
        return render_template('withdraw.html',
                                    exchanges = current_user.exchanges.all(),
                                    current_user=current_user,posts = Post.query.all(),
                                    notifications=current_user.notifications.all(),
                                    withdrawals = connectExchange().fetch_withdrawals(),
                               )
    else:
        return render_template('404.html')
    
#get all withdrawals history
@app.route('/api/v1/withdrawals/', methods=['POST','GET'])
@login_required
def crypto_withdrawals():
    '''
    the withdrawals are returned in the following format:
    [
        {
            "info": {
                "currency": "BTC",
                "amount": "0.0001",
                "txid": "5f7a0a9c03aa675e4a06f5b0",
                "address": "3J98t1WpEZ73CNmQviecrnyiWrnqRhWNLy",
                "addressTo": "3J98t1WpEZ73CNmQviecrnyiWrnqRhWNLy",
                "type": "withdrawal",
                "timestamp": "1601817600000",
                "status": "success"
            },
        }
    ]
    '''
    return jsonify(connectExchange().fetch_withdrawals())



@app.route('/api/v1/currencies/<exchange_name>', methods=['POST','GET'])
@login_required
def get_currencies(exchange_name):
    '''
    the currencies are returned in the following format:
    {
        "active": true,
        "code": "ETHW",
        "deposit": true,
        "fee": 0.01,
        "id": "ETHW",
        "limits": {
            "amount": {
                "max": null,
                "min": null
            },
            "deposit": {
                "max": null,
                "min": 0
            },
            "withdraw": {
                "max": null,
                "min": 0.01
            }
        },
        "name": "ETHW",
        "networks": {
            "ETHW": {
                "active": true,
                "deposit": true,
                "fee": 0.01,
                "id": "ETHW",
                "info": {
                    "chain": "ETHW",
                    "chainDeposit": "1",
                    "chainType": "ETHW",
                    "chainWithdraw": "1",
                    "confirmation": "50",
                    "depositMin": "0",
                    "minAccuracy": "8",
                    "withdrawFee": "0.01",
                    "withdrawMin": "0.01",
                    "withdrawPercentageFee": "0"
                },
                "limits": {
                    "deposit": {
                        "max": null,
                        "min": 0
                    },
                    "withdraw": {
                        "max": null,
                        "min": 0.01
                    }
                },
                "network": "ETHW",
                "precision": 1e-8,
                "withdraw": true
            }
        },
        "precision": 1e-8,
        "withdraw": true
    }
    '''
    exchange = connectExchange(exchange_name)
    if exchange.fetch_currencies() is None:
        return jsonify([])
    
    return jsonify(list(map(lambda x: x[1],exchange.fetch_currencies().items())))

@app.route('/api/v1/markets/<exchange_name>', methods=['POST','GET'])
@login_required
def get_markets(exchange_name):
    '''
    the markets are returned in the following format:
    {
        "base": {
            "1INCH": "1INCH",
            "1SOL": "1SOL",
            "3P": "3P",
            ...
        },
        "quote": {
            "BRZ": "BRZ",
            "BTC": "BTC",
            ...
        }
    }
    '''
    exchange = connectExchange(exchange_name)

    if exchange.fetch_markets() is None:
        return jsonify([])
    
    currencies = exchange.fetch_markets()
    return jsonify({"base": {key: value for key, value in zip([currency["base"] for currency in currencies], [currency["base"] for currency in currencies])}, "quote": {key: value for key, value in zip([currency["quote"] for currency in currencies], [currency["quote"] for currency in currencies])}})

@app.route('/api/v1/all_markets/<exchange_name>', methods=['POST','GET'])
@login_required
def get_all_markets(exchange_name):
    exchange = connectExchange(exchange_name)

    if exchange.fetch_markets() is None:
        return jsonify([])
    pairs = []
    for currency in exchange.fetch_markets():
        if currency['active'] and currency['spot']:
            pairs.append(currency['symbol'])

    return jsonify(pairs)

