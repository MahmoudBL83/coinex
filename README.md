# coinex

Sure! Here's an example of API documentation for the authentication part of your code:

## Authentication API

### Login

**Endpoint:** `/login`

**Method:** `POST`

**Description:** Authenticates a user and logs them into the system.

**Request Body:**

| Parameter | Type   | Required | Description            |
| --------- | ------ | -------- | ---------------------- |
| email     | string | Yes      | User's email address   |
| password  | string | Yes      | User's password        |
| remember  | string | No       | Flag to remember login |

**Response:**

- Success: Redirect to `/exchanges` (Status code: 302)
- Failure: Flash message with "Invalid email or password" (Status code: 200)

### Register

**Endpoint:** `/register`

**Method:** `POST`

**Description:** Registers a new user in the system.

**Request Body:**

| Parameter        | Type   | Required | Description                     |
| ---------------- | ------ | -------- | ------------------------------- |
| email            | string | Yes      | User's email address            |
| password         | string | Yes      | User's password                 |
| confirm_password | string | Yes      | Confirmation of user's password |

**Response:**

- Success: Flash message with "Registration successful" and redirect to `/login` (Status code: 302)
- Failure:
  - Passwords do not match: Flash message with "Passwords do not match" and redirect to `/register` (Status code: 302)
  - Email already taken: Flash message with "Email already taken" and redirect to `/register` (Status code: 302)

### Reset Password

**Endpoint:** `/reset_password`

**Method:** `POST`

**Description:** Sends a password reset email to the user.

**Request Body:**

| Parameter | Type   | Required | Description          |
| --------- | ------ | -------- | -------------------- |
| email     | string | Yes      | User's email address |

**Response:**

- Success: Flash message with "Instructions sent to email" and redirect to `/login` (Status code: 302)
- Failure: Flash message with "Email not found" (Status code: 200)

### Logout

**Endpoint:** `/logout`

**Method:** `GET`

**Description:** Logs out the currently authenticated user.

**Response:**

- Success: Redirect to `/exchanges` (Status code: 302)

Certainly! Here's an example of API documentation for the `/api/v1/user_info/` route:

## User Info API

### Retrieve User Information

**Endpoint:** `/api/v1/user_info/`

**Method:** `GET`

**Description:** Retrieves information about the user's account and portfolio.

**Headers:**

| Header        | Value           |
| ------------- | --------------- |
| Authorization | Bearer \<token> |

**Response:**

```json
{
  "balance": {
    "total": {
      "BTC": 0.5,
      "ETH": 2.0
    }
  },
  "exchanges": [
    {
      "id": 1,
      "name": "Binance",
      "api_key": "**********",
      "api_secret": "**********"
    },
    {
      "id": 2,
      "name": "Coinbase",
      "api_key": "**********",
      "api_secret": "**********"
    }
  ],
  "open_orders": [
    {
      "id": "123456789",
      "symbol": "BTC/USDT",
      "side": "buy",
      "price": 45000,
      "quantity": 0.1
    }
  ],
  "transactions": [
    {
      "id": "987654321",
      "symbol": "ETH/USDT",
      "type": "buy",
      "price": 3000,
      "quantity": 1.5
    }
  ],
  "overall_profit": 1500.0,
  "latest_30_days_profit_btc": 2500.0,
  "latest_30_days_profit_usd": 125000.0,
  "profit_percent_month": 5.0,
  "profit_percent_day": 0.16666666666666666,
  "sharpe_ratio": 1.25,
  "deviation": 0.03,
  "sortino_ratio": 2.5
}
```

**Response Description:**

- `balance`: The total balance of the user's account in BTC and ETH.
- `exchanges`: A list of exchanges connected to the user's account, including their IDs, names, API keys, and API secrets.
- `open_orders`: A list of open orders in the user's account, including their IDs, trading symbols, order side (buy/sell), price, and quantity.
- `transactions`: A list of recent transactions in the user's account, including their IDs, trading symbols, transaction type (buy/sell), price, and quantity.
- `overall_profit`: The overall profit or loss in the user's portfolio.
- `latest_30_days_profit_btc`: The profit or loss in the user's portfolio in BTC over the last 30 days.
- `latest_30_days_profit_usd`: The profit or loss in the user's portfolio in USD over the last 30 days.
- `profit_percent_month`: The profit percentage in the user's portfolio per month.
- `profit_percent_day`: The profit percentage in the user's portfolio per day.
- `sharpe_ratio`: The Sharpe ratio, a measure of risk-adjusted return.
- `deviation`: The standard deviation of the portfolio returns.
- `sortino_ratio`: The Sortino ratio, a measure of risk-adjusted return considering only downside risk.

**Error Responses:**

- Unauthorized: If the request does not include a valid access token in the `Authorization` header. Status code: 401

# API Documentation

## Deposit Endpoint

- URL: `/api/v1/deposit/`
- Methods: POST, GET
- Authentication: Login required

### POST Request

- Description: Process a cryptocurrency deposit.
- Body:
  - `symbol` (string): The symbol of the cryptocurrency.
  - `network` (string): The network to deposit the cryptocurrency on.

### GET Request

- Description: Render the deposit page.
- Response: HTML template with the list of exchanges and the current user.

## Transfer Endpoint

- URL: `/api/v1/transfer/`
- Methods: POST, GET
- Authentication: Login required

### POST Request

- Description: Perform a cryptocurrency transfer.
- Body:
  - `amount` (float): The amount of cryptocurrency to transfer.
  - `side` (string): The side of the transfer (e.g., 'buy', 'sell').
  - `symbol` (string): The symbol of the cryptocurrency.

### GET Request

- Description: Render the transfer page.
- Response: HTML template with the list of exchanges and the current user.

## Withdraw Endpoint

- URL: `/api/v1/withdraw/`
- Methods: POST, GET
- Authentication: Login required

### POST Request

- Description: Initiate a cryptocurrency withdrawal.
- Body:
  - `amount` (float): The amount of cryptocurrency to withdraw.
  - `recipient_address` (string): The recipient's address for the withdrawal.
  - `currency` (string): The currency to withdraw.
  - `network` (string): The network for the withdrawal.

### GET Request

- Description: Render the withdrawal page.
- Response: HTML template with the list of exchanges and the current user.

## Get Supported Currencies Endpoint

- URL: `/api/v1/currencies/<exchange_name>`
- Methods: POST, GET
- Authentication: Login required

### POST Request

- Description: Retrieve the list of supported currencies for a specific exchange.
- Body: None

### GET Request

- Description: Retrieve the list of supported currencies for a specific exchange.

## Get Supported Markets Endpoint

- URL: `/api/v1/markets/<exchange_name>`
- Methods: POST, GET
- Authentication: Login required

### POST Request

- Description: Retrieve the list of supported markets (trading pairs) for a specific exchange.
- Body: None

### GET Request

- Description: Retrieve the list of supported markets (trading pairs) for a specific exchange.

## Get All Active Markets Endpoint

- URL: `/api/v1/all_markets/<exchange_name>`
- Methods: POST, GET
- Authentication: Login required

### POST Request

- Description: Retrieve the list of all active spot markets (trading pairs) for a specific exchange.
- Body: None

### GET Request

- Description: Retrieve the list of all active spot markets (trading pairs) for a specific exchange.
