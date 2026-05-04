# Using Thunder Client with uctrade API ✅

## Importing
1. Open VS Code and the Thunder Client extension.
2. Click the Thunder icon → Collections → Import → choose `docs/thunder_collection_uctrade.json`.
3. Import the environment: Thunder → Environment → Import → `docs/thunder_env_uctrade.json`.

## Setup
- Set `{{baseUrl}}` to your running server (default: `http://localhost:8000`).
- To authenticate:
  1. Run **Register** request to create a user.
  2. Run **Get JWT token**; copy the `access` token into the environment variable `accessToken` (no `Bearer` prefix needed in value).
  3. Requests that need authentication include header: `Authorization: Bearer {{accessToken}}`.

## Useful requests included
- Register: `POST /api/users/register/` (JSON body: username, email, password, password2)
- Token: `POST /api/token/` (JSON: username, password) → returns `access` and `refresh` tokens. The collection includes a test script to auto-save tokens into the imported environment variables `accessToken` and `refreshToken`.
- List Courses: `GET /api/courses/`
- Create Course: `POST /api/courses/` (Auth: instructor)
- Upload Video: `POST /api/videos/` (form-data: file, title, course)
- Upload PDF: `POST /api/courses/materials/` (form-data: file, title, course) — new request added
- Notifications: `GET /api/notifications/` and `POST /api/notifications/` — new requests added
- Add to Cart: `POST /api/cart/` (JSON: course)
- Create PaymentIntent: `POST /api/payments/create-intent/` (JSON: order_id)
- Webhook Simulation: `POST /api/payments/webhook/` (JSON) — sample Stripe event request added for local testing
- Enroll Class: `POST /api/classes/{id}/enroll/` (Auth required)


## Tips
- For file upload requests, replace `path/to/video.mp4` with a real path on your machine.
- Use the Stripe CLI to send test webhook events to `/api/payments/webhook/` when testing payments.
- Add extra sample requests as needed for notifications, PDF uploads, and webhook simulation.

If you want, I can also generate a Postman collection or add more example responses and pre-request scripts (e.g., auto-save token into environment). 🔧
