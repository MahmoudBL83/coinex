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

Please note that this is just a basic example, and you may need to include additional details depending on your specific requirements. It's important to provide clear explanations of the endpoints, their methods, request parameters, responses, and any error conditions.
