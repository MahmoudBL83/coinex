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
