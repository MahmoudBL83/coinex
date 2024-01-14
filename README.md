# API Documentation for Crypto Bots Web App

## Authentication

### Register

#### `POST /register`

Register a new user.

##### Request
```json
{
  "email": "user@example.com",
  "firstName": "John",
  "lastName": "Doe",
  "password": "password123",
  "confirm_password": "password123"
}
```

##### Response
```json
{
  "message": "Registration successful. Please check your email to verify your account.",
  "ok": true
}
```

### Login

#### `POST /login`

Log in to the web app.

##### Request
```json
{
  "admin": true,
  "email": "admin",
  "password": "123"
}
```

##### Response
```json
{
  "message": "Admin logged in successfully",
  "ok": true
}
```

### Verify OTP

#### `POST /verify-otp`

Verify the OTP (One-Time Password) after login.

##### Request
```json
{
  "otp": "123456"
}
```

##### Response
```json
{
  "access_token": "your_access_token",
  "ok": true
}
```

### Resend OTP

#### `GET /resend_otp`

Resend the OTP.

##### Response
```json
{
  "message": "OTP resent"
}
```

### Verify Email

#### `GET /verify_email/:token`

Verify the user's email address.

##### Response
```
Email verification successful. You can now log in.
```

### Reset Password

#### `POST /reset_password`

Request to reset the password.

##### Request
```json
{
  "email": "user@example.com"
}
```

##### Response
```json
{
  "message": "Instructions sent to email",
  "ok": true
}
```

#### `POST /reset_password/:token`

Reset the password using the token received via email.

##### Request
```json
{
  "password": "new_password",
  "confirm_password": "new_password"
}
```

##### Response
```json
{
  "message": "Your Password has been changed",
  "ok": true
}
```

### Logout

#### `GET /logout`

Logout from the web app.

##### Response
Redirects to the exchanges page.

### Logout (API Version)

#### `POST /api/v1/logout`

Logout from the API.

##### Response
Redirects to the exchanges page.

### Logout Admin

#### `GET /logout_admin`

Logout the admin user.

##### Response
Redirects to the login page.

### Send Mail from Admin

#### `POST /send_mail_from_admin`

Send an email from the admin.

##### Request
```json
{
  "subject": "Email Subject",
  "body": "Email Body",
  "email": "optional_user_email"
}
```

##### Response
```json
{
  "message": "Email sent successfully",
  "ok": true
}
```

## User Dashboard

### User Info

#### `GET /api/v1/user_stats/`

Retrieve user statistics and information.

##### Response
```json
{
  "exchanges": [...],
  "open_orders": [...],
  "balance_history": "...",
  "transactions": [...],
  "balance_usd": 1000.00,
  "balance_btc": 0.05,
  "profit_monthly_btc": 0.02,
  "profit_monthly_usd": 200.00,
  "profit_daily_btc": 0.001,
  "profit_daily_usd": 10.00,
  "profit_monthly_percent_btc": 10.00,
  "profit_monthly_percent_usd": 5.00,
  "profit_daily_percent_btc": 2.00,
  "profit_daily_percent_usd": 1.00,
  "profit_overall_btc": 0.05,
  "profit_overall_usd": 500.00,
  "sharpe_ratio": 1.2,
  "sortino_ratio": 1.5,
  "deviation": 0.03,
  "not_supported_trans": [...]
}
```

### Edit User Info

#### `POST /api/v1/edit_user_info/`

Edit user profile image.

##### Request
```json
"base64_encoded_image"
```

### Reset Stats

#### `GET /api/v1/reset_stats`

Reset user statistics.

##### Response
```json
{
  "message": "your stats have been reset",
  "ok": true
}
```

### Assets

#### `GET /api/v1/assets`

Retrieve user assets.

##### Response
```json
[
  {
    "currency": "BTC",
    "free": 0.1,
    "used": 0.05,
    "total": 0.15,
    "price": 40000.00,
    "eqUSD": 6000.00
  },
  {
    "currency": "ETH",
    "free": 1.5,
    "used": 0.5,
    "total": 2.0,
    "price": 3000.00,
    "eqUSD": 6000.00
  },
  ...
]
```

## Knowledge Base

### Knowledge Base

#### `POST /knowledge_base`

Retrieve knowledge base articles.

##### Response
```json
{
  "posts": [...],
  "categories": [...]
}
```

### Knowledge Base by Category

#### `POST /knowledge_base_cat/:category_id`

Retrieve knowledge base articles by category.

##### Response
```json
{
  "posts": [...],
  "category": {...},
  "articles": [...],
  "ok": true,
  "message": "success"
}
```

### Knowledge Base Post

#### `POST /knowledge_base_post/:post_id`

Retrieve a knowledge base article by post ID.



##### Response
```json
{
  "post": {...},
  "posts": [...],
  "ok": true,
  "message": "success"
}
```

## User Profile and Settings

### User Profile

#### `GET /user/profile`

Retrieve user profile information.

### User Privacy Settings

#### `GET /user/setting`

Retrieve user privacy settings.

## Additional APIs

### Get Data

#### `GET /getData/`

Retrieve data for autocomplete functionality.

### Order Book History

#### `GET /api/v1/order_book_history`

Retrieve order book history.

### Last Trades History

#### `GET /api/v1/last_trades_history`

Retrieve last trades history.

### Live Balance

#### `GET /api/v1/live_balance`

Retrieve live balance for a specific symbol.

### Live Balance JSON

#### `GET /api/v1/live_balance_json`

Retrieve live balance in JSON format.

### Live Price

#### `GET /api/v1/live_price`

Retrieve live price for a specific symbol.

### Market Table

#### `GET /api/v1/market_table`

Retrieve the market table.

### Live Crypto Data

#### `GET /api/v1/live_crypto_data`

Retrieve live cryptocurrency data.

### Indicators

#### `GET /api/v1/indicators`

Retrieve indicators for a specific symbol.

### Indicators Signals

#### `GET /api/v1/indicators_signals`

Retrieve indicators signals for a given interval and exchange.

### User Settings IP Check

#### `POST /api/v1/user_settings/ip_check`

Update the user's IP check settings.

##### Request
```json
{
  "isActive": true
}
```

## Smart Trade

### Get Smart Trades

#### `GET /api/v1/smart_trades/`

Retrieve all smart trades for the current user.

##### Response
```json
{
  "smart_trades": [
    {
      "id": 1,
      "trade_type": "Smart Trade",
      "exchange": "Binance",
      "base_currency": "BTC",
      "quote_currency": "USDT",
      "units": 1.0,
      "amount": 100.0,
      "buy_price": 40000.0,
      "buy_trigger_price": 38000.0,
      "stop_loss": true,
      "take_profit": true,
      "tpTriggerType": "market",
      "order_type": "limit",
      "buy_order_id": "12345",
      "trailing_order_id": "54321",
      "stop_loss_id": "67890",
      "last_take_profit_id": "98765",
      "trailing_take_profit": true,
      "trailing_deviation": 0.03,
      "trailing_stop_loss": true,
      "stop_loss_price_percent": 2.0,
      "stop_loss_price": 37000.0,
      "stop_loss_type": "limit",
      "stop_loss_time_out": true,
      "stop_loss_time_out_time": 10,
      "deal_started": true,
      "move_to_break_even": true,
      "isActive": true,
      "last_price": 41000.0,
      "bought_price": 40000.0,
      "use_assets": true,
      "total_profit": 50.0
    },
    ...
  ]
}
```

### Create Smart Trade

#### `POST /api/v1/smart_trades/`

Create a new smart trade.

##### Request
```json
{
  "trade_type": "Smart Trade",
  "exchange": "Binance",
  "symbol": "BTC/USDT",
  "price": 40000.0,
  "triggerPrice": 38000.0,
  "buy_type": "limit",
  "amount": 100.0,
  "take_profits": true,
  "tpTriggerType": "market",
  "tpTriggerPxType": "absolute",
  "stop_loss": true,
  "take_profit": true,
  "stop_loss_type": "limit",
  "stop_loss_price_percent": 2.0,
  "stop_loss_price": 37000.0,
  "trailing_take_profit": true,
  "trailing_stop_loss": true,
  "trailing_deviation": 0.03,
  "stop_loss_time_out": true,
  "stop_loss_time_out_time": 10,
  "exchange": "Binance",
  "move_to_break_even": true,
  "use_assets": true
}
```

##### Response
```json
{
  "message": "Smart Trade executed successfully.",
  "ok": true
}
```

### Edit Smart Trade

#### `POST /api/v1/smart_trades/edit/<int:smart_trade_id>`

Edit an existing smart trade.

##### Request
```json
{
  "trade_type": "Smart Trade",
  "symbol": "BTC/USDT",
  "price": 42000.0,
  "triggerPrice": 40000.0,
  "buy_type": "limit",
  "amount": 150.0,
  "take_profits": true,
  "tpTriggerType": "market",
  "stop_loss": true,
  "take_profit": true,
  "stop_loss_type": "limit",
  "stop_loss_price_percent": 2.5,
  "stop_loss_price": 38000.0,
  "trailing_take_profit": true,
  "trailing_stop_loss": true,
  "trailing_deviation": 0.02,
  "stop_loss_time_out": true,
  "stop_loss_time_out_time": 15,
  "exchange": "Binance",
  "move_to_break_even": true,
  "use_assets": true
}
```

##### Response
```json
{
  "message": "Smart trade edited successfully",
  "ok": true
}
```

### Open Smart Trade

#### `POST /api/v1/smart_trades/open/<int:smart_trade_id>`

Open a previously closed smart trade.

##### Response
```json
{
  "message": "Smart trade opened successfully",
  "ok": true
}
```

### Run Smart Trade

#### `POST /api/v1/smart_trades/run/<int:smart_trade_id>`

Run a smart trade again.

##### Response
```json
{
  "message": "Smart trade ran again successfully",
  "ok": true
}
```

### Close Smart Trade

#### `POST /api/v1/smart_trades/close/<int:smart_trade_id>`

Close a smart trade.

##### Response
```json
{
  "message": "Smart trade closed successfully",
  "ok": true
}
```

### Cancel Smart Trade

#### `POST /api/v1/smart_trades/cancel/<int:smart_trade_id>`

Cancel a smart trade.

##### Response
```json
{
  "message": "Smart trade cancelled successfully",
  "ok": true
}
```

### Get Smart Trade by ID

#### `GET /api/v1/smart_trades/<int:id>`

Retrieve a smart trade by ID.

##### Response
```json
{
  "smart_trade": {
    "id": 1,
    "trade_type": "Smart Trade",
    "exchange": "Binance",
    "base_currency": "BTC",
    "quote_currency": "USDT",
    "units": 1.0,
    ...
  }
}
```

### Update Smart Trade

#### `PUT /api/v1/smart_trades/<int:id>`

Update a smart trade by ID.

##### Request
```json
{
  "name": "Updated Smart Trade Name",
  "strategy": "Updated Smart Trade Strategy",
  "exchange": "Updated Exchange",
  ...
}
```

##### Response
```json
{
  "smart_trade": {
    "id": 1,
    "name": "Updated Smart Trade Name",
    "strategy": "Updated Smart Trade Strategy",
    "exchange": "Updated Exchange",
    ...
  }
}
```

### Delete Smart Trade

#### `DELETE

 /api/v1/smart_trades/<int:id>`

Delete a smart trade by ID.

##### Response
```json
{
  "message": "Smart trade with ID 1 has been deleted",
  "ok": true
}
```

Please ensure to replace placeholder values with actual data when making requests.
