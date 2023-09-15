# API Routes

## Login

- **URL:** `/login`
- **Methods:** `GET`, `POST`
- **Description:** This route is used for user authentication and login.
- **Request Parameters:**
  - `email` (string): The user's email.
  - `password` (string): The user's password.
  - `remember` (optional, boolean): Indicates whether to remember the user's session.
- **Response:**
  - If the login is successful, the user will be redirected to the `exchanges` route.
  - If the login fails, an error message will be flashed and the user will be redirected to the `sign-in.html` template.

## Verify OTP

- **URL:** `/verify-otp`
- **Methods:** `GET`, `POST`
- **Description:** This route is used for OTP (One-Time Password) verification.
- **Request Parameters:**
  - `otp` (string): The OTP entered by the user.
- **Response:**
  - If the OTP is valid, the user will be redirected to the `exchanges` route.
  - If the OTP is invalid, an error message will be flashed and the user will be redirected to the `verify_otp2.html` template.

## Resend OTP

- **URL:** `/resend_otp`
- **Methods:** `GET`
- **Description:** This route is used to resend the OTP to the user's email.
- **Response:**
  - If the email is found in the session, a new OTP will be generated and sent to the user's email.
  - If the email is not found in the session, the user will be redirected to the `verify_otp` route.

## Register

- **URL:** `/register`
- **Methods:** `GET`, `POST`
- **Description:** This route is used for user registration.
- **Request Parameters:**
  - `email` (string): The user's email.
  - `firstName` (string): The user's first name.
  - `lastName` (string): The user's last name.
  - `password` (string): The user's password.
  - `confirm_password` (string): The confirmation password.
- **Response:**
  - If the registration is successful, the user will be redirected to the `login` route.
  - If there are any errors (e.g., passwords do not match or email already taken), appropriate error messages will be flashed, and the user will be redirected to the `register` route.

## Reset Password (Token)

- **URL:** `/reset_password/<token>`
- **Methods:** `GET`, `POST`
- **Description:** This route is used for resetting the user's password using a token.
- **Request Parameters:**
  - `password` (string): The new password.
  - `confirm_password` (string): The confirmation password.
- **Response:**
  - If the password reset is successful, a success message will be returned as JSON.
  - If there are any errors (e.g., passwords do not match or invalid/expired token), an appropriate error message will be returned as JSON.

## Reset Password

- **URL:** `/reset_password`
- **Methods:** `GET`, `POST`
- **Description:** This route is used for initiating the password reset process.
- **Request Parameters:**
  - `email` (string): The user's email.
- **Response:**
  - If the email is found, instructions will be sent to the user's email.
  - If the email is not found, an error message will be returned as JSON.

## Logout

- **URL:** `/logout`
- **Methods:** `GET`
- **Description:** This route is used for user logout.
- **Response:**
  - The user will be logged out and redirected to the `exchanges` route.

## User Stats

- **URL:** `/api/v1/user_stats/`
- **Methods:** `GET`, `POST`
- **Description:** This route is used to retrieve user statistics and information.
- **Request Parameters:**
  - `exchange_name` (optional, string): The name of the exchange for which to retrieve data.
  - `user_id` (optional, int): The ID of the user for whom to retrieve data.
- **Response:**
  - Returns a JSON object containing the user's exchanges, open orders, transactions, balances, profits, ratios, and deviation.

## Edit User Info

- **URL:** `/api/v1/edit_user_info/`
- **Methods:** `POST`
- **Description:** This route is used to edit the user's profile image.
- **Request Parameters:**
  - `data` (string): The user's new profile image, encoded as UTF-8.
- **Response:**
  - Updates the user's profile image in the database.

## Reset Stats

- **URL:** `/api/v1/reset_stats/`
- **Methods:** `GET`
- **Description:** This route is used to reset the user's statistics.
- **Response:**
  - Returns a JSON object with a success message indicating that the user's stats have been reset.

## Assets

- **URL:** `/api/v1/assets/`
- **Methods:** `GET`
- **Description:** This route is used to retrieve the user's assets and balances.
- **Query Parameters:**
  - `exchange` (string): The name of the exchange for which to retrieve assets. Use "all" to get assets from all exchanges.
- **Response:**
  - Returns a JSON object containing the user's assets, including currency, free balance, used balance, total balance, price, and equivalent USD value.

## Get Exchanges

- **URL:** `/api/v1/exchanges/`
- **Methods:** `GET`
- **Description:** This route is used to retrieve all exchanges linked to the user's account.
- **Response:**
  - Returns a JSON object containing the user's linked exchanges.

## Connect Exchange

- **URL:** `/api/v1/connect/`
- **Methods:** `POST`
- **Description:** This route is used to connect to a new exchange by providing API credentials.
- **Request Parameters:**
  - `api_key` (string): The API key for the exchange.
  - `api_secret` (string): The API secret for the exchange.
  - `exchange_name` (string): The name of the exchange to connect to.
  - `password` (string): The password for the exchange (optional).
  - `demo` (boolean): Whether to use the exchange's sandbox/demo mode (optional).
- **Response:**
  - Returns a JSON object with the status of the connection attempt.

## Disconnect Exchange

- **URL:** `/api/v1/disconnect/`
- **Methods:** `POST`
- **Description:** This route is used to disconnect from a linked exchange.
- **Request Parameters:**
  - `exchange_name` (string): The name of the exchange to disconnect from.
- **Response:**
  - Returns a JSON object with the status of the disconnection attempt.

## Favorite Exchange

- **URL:** `/api/v1/fav_exchange/`
- **Methods:** `POST`
- **Description:** This route is used to set a favorite exchange for the user.
- **Request Parameters:**
  - `exchange_name` (string): The name of the exchange to set as the favorite.
- **Response:**
  - Returns a JSON object confirming that the specified exchange is now the user's favorite.

## Trading

1. `place_order()`:
   - Route: `/api/v1/order/` (POST method)
   - Functionality: Places an order on the cryptocurrency exchange.
   - Parameters:
     - `symbol`: Symbol of the order.
     - `type`: Type of the order (limit or market).
     - `order_price`: Price of the order (optional).
     - `trigger_price`: Trigger price for conditional orders (optional).
     - `amount`: Amount of the order.
     - `side`: Side of the order (buy or sell).
   - Returns: JSON response with the order details if successful, or an error message if an exception occurs.

2. `cancel_order()`:
   - Route: `/api/v1/order/cancel` (POST method)
   - Functionality: Cancels an order on the cryptocurrency exchange.
   - Parameters:
     - `id`: ID of the order.
     - `symbol`: Symbol of the order.
   - Returns: JSON response indicating whether the cancellation was successful or not.

3. `history_open_orders()`:
   - Route: `/api/v1/history/open_orders/` (GET and POST methods)
   - Functionality: Retrieves the user's open orders history from the cryptocurrency exchange.
   - Returns: returns JSON response with paginated open orders.

4. `history_orders()`:
   - Route: `/api/v1/history/orders/` (GET and POST methods)
   - Functionality: Retrieves the user's closed orders history from the cryptocurrency exchange.
   - Returns: returns JSON response with paginated closed orders.

4. `history_trades()`:
   - Route: `/api/v1/history/trades/` (GET and POST methods)
   - Functionality: Retrieves the user's trades history from the cryptocurrency exchange.
   - Returns: returns JSON response with paginated closed orders.

Sure! Here's the API documentation for the routes mentioned in the code:

---

## Get Smart Trades

Retrieves all smart trades for the current user.

### Request

- Method: GET
- URL: `/api/v1/smart_trades/`

### Response

- Body:
  ````json
  {
    "smart_trades": [
      {
        "trade_type": "string",
        "exchange": "string",
        "base_currency": "string",
        "quote_currency": "string",
        "units": "float",
        "amount": "float",
        "user_id": "integer",
        "buy_price": "float",
        "buy_trigger_price": "float",
        "stop_loss": "string",
        "take_profit": "string",
        "take_profit_quantities": "array",
        "tpTriggerType": "string",
        "order_type": "string",
        "buy_order_id": "integer",
        "trailing_order_id": "integer",
        "trailing_take_profit": "string",
        "trailing_deviation": "float",
        "trailing_stop_loss": "string",
        "stop_loss_price_percent": "float",
        "stop_loss_price": "float",
        "stop_loss_type": "string",
        "stop_loss_time_out": "string",
        "stop_loss_time_out_time": "integer",
        "deal_started": "boolean"
      },
      ...
    ]
  }
  ```

---

## Create Smart Trade

Creates a new smart trade.

### Request

- Method: POST
- URL: `/api/v1/smart_trades/`
- Body:
  ````json
  {
    "trade_type": "string",
    "symbol": "string",
    "price": "float",
    "triggerPrice": "float",
    "buy_type": "string",
    "amount": "float",
    "take_profits": "array",
    "tpTriggerType": "string",
    "tpTriggerPxType": "string",
    "stop_loss": "string",
    "take_profit": "string",
    "stop_loss_type": "string",
    "stop_loss_trigger_price": "float",
    "stop_loss_price": "float",
    "stop_loss_price_percent": "float",
    "trailing_take_profit": "string",
    "trailing_stop_loss": "string",
    "trailing_deviation": "float",
    "stop_loss_time_out": "string",
    "stop_loss_time_out_time": "integer",
    "exchange": "string"
  }
  ```

### Response

- Body:
  ````json
  {
    "message": "string",
    "ok": "boolean"
  }
  ```

---

## Edit Smart Trade
- Route: `/api/v1/smart_trades/edit/<int:smart_trade_id>`
- Method: `POST`

### Request Body
- `trade_type` (string)
- `symbol` (string)
- `price` (float)
- `triggerPrice` (float)
- `buy_type` (string)
- `amount` (float)
- `stop_loss` (string)
- `take_profit` (string)
- `tpTriggerType` (string)
- `stop_loss_type` (string)
- `stop_loss_trigger_price` (float)
- `stop_loss_price_percent` (float)
- `trailing_take_profit` (string)
- `trailing_stop_loss` (string)
- `trailing_deviation` (float)
- `stop_loss_time_out` (string)
- `stop_loss_time_out_time` (int)
- `exchange` (string)

### Response
- Success: 200 OK
  - Content-Type: application/json
  - Body: `{'message': 'Smart trade edited successfully', 'ok': True}`
- Error: 404 Not Found
  - Content-Type: application/json
  - Body: `{'message': 'Smart trade not found'}`

## Open Smart Trade
- Route: `/api/v1/smart_trades/open/<int:smart_trade_id>`
- Method: `POST`

### Response
- Success: 200 OK
  - Content-Type: application/json
  - Body: `{'message': 'Smart trade opened successfully', 'ok': True}`
- Error: 404 Not Found
  - Content-Type: application/json
  - Body: `{'message': 'Smart trade not found'}`

## Close Smart Trade
- Route: `/api/v1/smart_trades/close/<int:smart_trade_id>`
- Method: `POST`

### Response
- Success: 200 OK
  - Content-Type: application/json
  - Body: `{'message': 'Smart trade closed successfully', 'ok': True}`
- Error: 404 Not Found
  - Content-Type: application/json
  - Body: `{'message': 'Smart trade not found'}`

## Cancel Smart Trade
- Route: `/api/v1/smart_trades/cancel/<int:smart_trade_id>`
- Method: `POST`

### Response
- Success: 200 OK
  - Content-Type: application/json
  - Body: `{'message': 'Smart trade cancelled successfully', 'ok': True}`
- Error: 404 Not Found
  - Content-Type: application/json
  - Body: `{'message': 'Smart trade not found'}`

## Get Smart Trade
- Route: `/api/v1/smart_trades/<int:id>`
- Method: `GET`

### Response
- Success: 200 OK
  - Content-Type: application/json
  - Body: Serialized smart trade object
- Error: 404 Not Found
  - Content-Type: application/json
  - Body: `{'error': 'Smart trade with ID {id} does not exist or does not belong to this user'}`

## Update Smart Trade
- Route: `/api/v1/smart_trades/<int:id>`
- Method: `PUT`

### Request Body
- `name` (string)
- `strategy` (string)
- `exchange` (string)
- `base_currency` (string)
- `quote_currency` (string)
- `allocation` (float)
- `conditions` (string)

### Response
- Success: 200 OK
  - Content-Type: application/json
  - Body: Serialized updated smart trade object
- Error: 404 Not Found
  - Content-Type: application/json
  - Body: `{'error': 'Smart trade with ID {id} does not exist or does not belong to this user'}`

## Delete Smart Trade
- Route: `/api/v1/smart_trades/<int:id>`
- Method: `DELETE`

### Response
- Success: 200 OK
  - Content-Type: application/json
  - Body: `{'message': 'Smart trade with ID {id} has been deleted'}`
- Error: 404 Not Found
  - Content-Type: application/json
  - Body: `{'error': 'Smart trade with ID {id} does not exist or does not belong to this user'}`
 
I apologize for the misunderstanding. Here's the updated Markdown document with the added API route:


## BOTS

### Create Bot

- URL: `/api/v1/create_bot/`
- Method: POST, GET
- Authentication: login_required

#### Request Body

```json
{
  "exchange_name": "<exchange_name>",
  "amount": <amount>,
  "amount_type": <amount_type>,
  "start_order_type": "<start_order_type>",
  "symbol": "<symbol>",
  "symbols": "<symbols>",
  "pair_type": "<pair_type>",
  "conds": "<conds>",
  "tp_type": "<tp_type>",
  "tp_percent": <tp_percent>,
  "tp_percent_type": "<tp_percent_type>",
  "profit_currency": "<profit_currency>",
  "tp_conds": "<tp_conds>",
  "trailing_take_profit": "<trailing_take_profit>",
  "trailing_deviation": <trailing_deviation>,
  "trailing_stop_loss": "<trailing_stop_loss>",
  "stop_loss_price_percent": <stop_loss_price_percent>,
  "stop_loss_time_out": "<stop_loss_time_out>",
  "stop_loss_time_out_time": <stop_loss_time_out_time>,
  "Close_deal_after_timeout": "<Close_deal_after_timeout>",
  "timeout": <timeout>,
  "timeout_type": <timeout_type>,
  "safety_orders_size": <safety_orders_size>,
  "safety_orders_size_scale": <safety_orders_size_scale>,
  "safety_orders_deviation": <safety_orders_deviation>,
  "safety_orders_deviation_scale": <safety_orders_deviation_scale>,
  "safety_orders_count": <safety_orders_count>,
  "safety_orders_count_max_active": <safety_orders_count_max_active>,
  "safety_orders_size_type": <safety_orders_size_type>,
  "min_profit": "<min_profit>",
  "min_profit_type": "<min_profit_type>",
  "min_profit_percent": <min_profit_percent>,
  "close_deal_action": "<close_deal_action>",
  "cooldown_between_deals": <cooldown_between_deals>,
  "open_deals_and_stop": <open_deals_and_stop>,
  "min_volume": <min_volume>,
  "max_price": <max_price>,
  "min_price": <min_price>
}
```

#### Response

```json
{
  "message": "Bot created successfully. Bot ID: <bot_id>",
  "ok": true
}
```

Sure! Here are the additional API routes documented in Markdown format:

```markdown
### Bots

- URL: `/bots/`
- Method: POST, GET
- Authentication: login_required

#### Request

This route accepts both POST and GET requests. If a POST request is made, it will return a JSON response containing the user's bots. If a GET request is made, it will render the 'bots.html' template, passing along the user's bots, notifications, exchanges, symbol, exchange, current_user, and posts as variables.

#### Response (POST)

```json
{
  "bots": [
    {
      "bot_id": "<bot_id_1>",
      "bot_name": "<bot_name_1>",
      ...
    },
    {
      "bot_id": "<bot_id_2>",
      "bot_name": "<bot_name_2>",
      ...
    },
    ...
  ]
}
```

### Bot Create

- URL: `/bot_create/`
- Method: GET
- Authentication: login_required

#### Request

This route renders the 'bots_create.html' template, passing along the pairs, notifications, exchanges, symbol, exchange, current_user, and posts as variables.

### Toggle Bot

- URL: `/api/v1/toggle_bot`
- Method: POST, GET
- Authentication: login_required

#### Request Body

```json
{
  "bot_id": "<bot_id>",
  "state": true
}
```

This route toggles the state of the specified bot based on the provided bot_id and state.

### Delete Bot

- URL: `/api/v1/delete_bot`
- Method: POST, GET
- Authentication: login_required

#### Request Body

```json
{
  "bot_id": "<bot_id>"
}
```

This route deletes the specified bot based on the provided bot_id.

#### Response

```json
{
  "message": "Bot deleted successfully. Bot ID: <bot_id>",
  "ok": true
}
```

### Get Bot Stats

- URL: `/api/v1/get_bot_stats`
- Method: POST, GET
- Authentication: login_required

#### Request Parameters

- bot_id: The ID of the bot to retrieve stats for.

#### Response

```json
{
  "isActive": true,
  "deal_started": true,
  "take_profit": "<take_profit_value>",
  "trailing_take_profit": "<trailing_take_profit_value>",
  "trailing_stop_loss": "<trailing_stop_loss_value>",
  "units": "<units_value>",
  "amount": <amount_value>,
  "sell_price": <sell_price_value>,
  "stop_loss_price": <stop_loss_price_value>,
  "buy_price": <buy_price_value>,
  "stop_loss_price_percent": <stop_loss_price_percent_value>,
  "stop_loss_time_out": <stop_loss_time_out_value>,
  "stop_loss_time_out_time": <stop_loss_time_out_time_value>,
  "exchange": "<exchange_value>",
  "base_currency": "<base_currency_value>",
  "quote_currency": "<quote_currency_value>",
  "strategy": "<strategy_value>",
  "name": "<name_value>",
  "id": "<bot_id>",
  "tp_price": "<tp_price_value>",
  "price_now": "<price_now_value>",
  "total_trades": <total_trades_value>
}
```

## IMPORTANT DATA
### Order Book History

- URL: `/api/v1/order_book_history`
- Method: GET
- Authentication: Not required

#### Request Parameters

- exchange: The name of the exchange.
- market: The name of the market.
- pair: The trading pair.

#### Response

Returns a boolean value indicating the success of the operation. Emits a socket.io event called `last_order` with the order book data if successful.

### Last Trades History

- URL: `/api/v1/last_trades_history`
- Method: GET
- Authentication: Not required

#### Request Parameters

- exchange: The name of the exchange.
- market: The name of the market.
- pair: The trading pair.

#### Response

Returns a boolean value indicating the success of the operation. Emits a socket.io event called `last_trade` with the last trade data if successful.

### Live Balance

- URL: `/api/v1/live_balance`
- Method: GET
- Authentication: Not required

#### Request Parameters

- exchange: The name of the exchange.
- symbol: The symbol to get the balance for.

#### Response

Returns the live balance for the specified symbol on the exchange.

### Live Price

- URL: `/api/v1/live_price`
- Method: GET
- Authentication: Not required

#### Request Parameters

- exchange: The name of the exchange.
- market: The name of the market.
- pair: The trading pair.
- stream: Optional. Set to "true" to enable streaming of live price data.

#### Response

Returns the live price for the specified trading pair on the exchange. If the `stream` parameter is set to "true", it emits a socket.io event called `live_price` with the live price data.

### Live Crypto Data

- URL: `/api/v1/live_crypto_data`
- Method: GET
- Authentication: Not required

#### Request Parameters

- exchange: The name of the exchange.
- market: The name of the market.
- pair: The trading pair.

#### Response

Returns live crypto data for the specified trading pair on the exchange. The response includes price and volume data.

### Indicators

- URL: `/api/v1/indicators`
- Method: GET
- Authentication: Not required

#### Request Parameters

- exchange: The name of the exchange.
- market: The name of the market.
- pair: The trading pair.
- interval: The time interval for the indicators.

#### Response

Returns a boolean value indicating the success of the operation. Emits a socket.io event called `indicators` with the calculated indicators data if successful.

### Indicators Signals

- URL: `/api/v1/indicators_signals`
- Method: GET
- Authentication: login_required

#### Request Parameters

- interval: The time interval for the indicators.
- exchange: The name of the exchange.

#### Response

Calculates and returns the signals for the specified interval and exchange, based on the available trading pairs.

Sure! Here's the API documentation for the additional routes:

## Get Currencies

- URL: `/api/v1/currencies/<exchange_name>`
- Method: POST, GET
- Authentication: login_required

### Request Parameters

- exchange_name: The name of the exchange.

### Response

Returns the list of currencies supported by the specified exchange in the following format:

```json
[
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
    },
    ...
]
```

## Get Markets

- URL: `/api/v1/markets/<exchange_name>`
- Method: POST, GET
- Authentication: login_required

### Request Parameters

- exchange_name: The name of the exchange.

### Response

Returns the list of markets supported by the specified exchange in the following format:

```json
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
```

## Get All Markets

- URL: `/api/v1/all_markets/<exchange_name>`
- Method: POST, GET
- Authentication: login_required

### Request Parameters

- exchange_name: The name of the exchange.

### Response

Returns the list of all active spot markets supported by the specified exchange. The response is a JSON array of trading pairs.

Example response:

```json
[
    "BTC/USDT",
    "ETH/USDT",
    ...
]
```
