from flask import render_template, request, redirect, url_for, jsonify,Response
import ccxt
from flask_login import login_required,current_user
from crypto import app,db,socketio,celery
from crypto.models import User, Exchange, SmartTrade, Bot, SafetyOrder, Post, Category
from crypto.notify import send_notification
from websocket import create_connection

@app.route('/exchanges')
@login_required
def exchanges():
    #exchange = connectExchange()
    return render_template("exchanges.html",exchanges = current_user.exchanges.all(),current_user=current_user,notifications=current_user.notifications.all(),posts = Post.query.all())

@app.route('/api/v1/exchanges/')
@login_required
def get_exchanges():
    # return all exchanges of user by its id as api from outside the flask app
    return jsonify([exchange.to_dict() for exchange in current_user.exchanges.all()])

# Define an endpoint to connect to an exchange
@app.route('/api/v1/connect/', methods=['POST'])
def connect_exchange():
    # Parse the API key and secret from the request body
    api_key = request.json['api_key']
    secret_key = request.json['api_secret']
    exchange_name = request.json['exchange_name']
    password = request.json['password']
    demo = request.json['demo']
    exchange = None
    
    # Initialize the exchange API client with the provided credentials
    if password:
        exchange = getattr(ccxt, exchange_name)({
            'apiKey': api_key,
            'secret': secret_key,
            'password':password,
        })
    else:
        exchange = getattr(ccxt, exchange_name)({
            'apiKey': api_key,
            'secret': secret_key,
        })
    if demo:
        exchange.set_sandbox_mode(True)

    try:
        exchange.load_markets()
        exchange.fetch_balance()
        
        activeExchange = Exchange(api_key=api_key,api_secret=secret_key,name=exchange_name,password=password,demo=demo,isActive=True)
        activeExchange.set_creds(api_key,secret_key,password)

        if len(current_user.exchanges.filter(Exchange.isActive==True).all())==0:
            activeExchange.isActive = True

        db.session.add(activeExchange)
        current_user.exchanges.append(activeExchange)
        current_user.exchange = exchange_name
        db.session.commit()
        return jsonify({
            'status': 'success',
            'message': f'Connected to {exchange_name} API',
            'ok': True,
        })
    except ccxt.AuthenticationError:
        return jsonify({
            'status': 'error',
            'message': 'Invalid API credentials',
        })
    except ccxt.ExchangeError:
        return jsonify({
            'status': 'error',
            'message': f'Failed to connect to {exchange_name} API',
        })

    except ccxt.NetworkError as network_error:
        return jsonify({
            'status': 'error',
            'message': 'Network error occurred',
        })
    except ccxt.RequestTimeout as timeout_error:
        return jsonify({
            'status': 'error',
            'message': 'Request timeout',
        })
    except ccxt.ExchangeNotAvailable as unavailable_error:
        return jsonify({
            'status': 'error',
            'message': 'Exchange not available',
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': 'An unexpected error occurred',
        })
    

# Define an endpoint to disconnect from an exchange
@app.route('/api/v1/disconnect/', methods=['POST'])
def disconnect_exchange():
        exchange_name = request.json['exchange_name']
        db.session.delete(current_user.exchanges.filter(Exchange.name==exchange_name).first())
        db.session.commit()
        return jsonify({
            'status': 'success',
            'message': f'discineected from {exchange_name} API',
        })

# Define an endpoint to get the user's connected exchanges
@app.route('/api/v1/fav_exchange/', methods=['POST'])
def fav_exchange():
    exchange_name = request.json['exchange_name']
    exchanges = current_user.exchanges.all()
    for exchange in exchanges:
        exchange.isActive = False

    current_user.exchanges.filter_by(name=exchange_name).first().isActive = True
    current_user.exchange = exchange_name
    db.session.commit()
    return jsonify({
        'status': 'success',
        'message': f'{exchange_name} is now your favorite exchange',
    })

def connectExchange(exchange_name=None):
    if exchange_name is None:
        if current_user.exchanges.filter(Exchange.isActive==True).first():
            exchange_name = current_user.exchanges.filter(Exchange.isActive==True).first().name
        else:
            return redirect(url_for('exchanges'))
    api_key,api_secret,password = current_user.exchanges.filter(Exchange.name==exchange_name).first().get_creds()
    if current_user.exchanges.filter(Exchange.name==exchange_name).first().password:
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

    if current_user.exchanges.filter(Exchange.name==exchange_name).first().demo:
            exchange.set_sandbox_mode(True)
    
    return exchange