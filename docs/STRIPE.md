# Stripe integration & local simulation

This project supports a local Stripe simulation mode so you can run payment flows without real Stripe credentials.

Behaviour:
- If `STRIPE_SECRET_KEY` is not set and `DEBUG=True`, the `/api/payments/create-intent/` endpoint will return a simulated PaymentIntent with:
  - `client_secret`: `test_cs_{order_id}`
  - provider payment id: `test_pi_{order_id}`
- This allows running end-to-end flows (create intent -> webhook => order marked paid) during local development and in our test suite without contacting Stripe.

Recommended local testing with Stripe CLI:
- If you want to test with real Stripe test keys:
  1. Set `STRIPE_SECRET_KEY=sk_test_...` and `STRIPE_WEBHOOK_SECRET=whsec_...` in your `.env`.
  2. Run `stripe listen --forward-to localhost:8000/api/payments/webhook/` and use `stripe trigger payment_intent.succeeded` to send events.

CI notes:
- The tests included in `tests/` use the simulated mode (no external network calls). If you enable real Stripe keys in CI, consider mocking Stripe calls or using the Stripe CLI as part of CI.
