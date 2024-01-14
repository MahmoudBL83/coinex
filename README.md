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

## Disclaimer

The API documentation is subject to change, and additional endpoints may be added or existing ones modified for better functionality. Always refer to the latest documentation for accurate information.
