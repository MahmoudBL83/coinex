Certainly! Here's the rearranged API documentation:

# API Documentation for Crypto Bots Web App

## Register

### `POST /register`

#### Request
```json
{
  "email": "user@example.com",
  "firstName": "John",
  "lastName": "Doe",
  "password": "password123",
  "confirm_password": "password123"
}
```

#### Response
```json
{
  "message": "Registration successful. Please check your email to verify your account.",
  "ok": true
}
```

## Login

### `POST /login`

#### Request
```json
{
  "admin": true,
  "email": "admin",
  "password": "123"
}
```

#### Response
```json
{
  "message": "Admin logged in successfully",
  "ok": true
}
```

## Verify OTP

### `POST /verify-otp`

#### Request
```json
{
  "otp": "123456"
}
```

#### Response
```json
{
  "access_token": "your_access_token",
  "ok": true
}
```

## Resend OTP

### `GET /resend_otp`

#### Response
```json
{
  "message": "OTP resent"
}
```

## Verify Email

### `GET /verify_email/:token`

#### Response
```
Email verification successful. You can now log in.
```

## Reset Password

### `POST /reset_password`

#### Request
```json
{
  "email": "user@example.com"
}
```

#### Response
```json
{
  "message": "Instructions sent to email",
  "ok": true
}
```

### `POST /reset_password/:token`

#### Request
```json
{
  "password": "new_password",
  "confirm_password": "new_password"
}
```

#### Response
```json
{
  "message": "Your Password has been changed",
  "ok": true
}
```

## Logout

### `GET /logout`

#### Response
Redirects to the exchanges page.

## Logout (API Version)

### `POST /api/v1/logout`

#### Response
Redirects to the exchanges page.

## Logout Admin

### `GET /logout_admin`

#### Response
Redirects to the login page.

## Send Mail from Admin

### `POST /send_mail_from_admin`

#### Request
```json
{
  "subject": "Email Subject",
  "body": "Email Body",
  "email": "optional_user_email"
}
```

#### Response
```json
{
  "message": "Email sent successfully",
  "ok": true
}
```

```
Note: Replace placeholders like `:token` and `your_access_token` with actual values.
```

Feel free to adjust the documentation based on your specific requirements and add more details as needed.
