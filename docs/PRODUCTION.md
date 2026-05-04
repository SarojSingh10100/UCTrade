# Production deployment notes ✅

Key settings to configure via environment variables (prefer a secrets manager):

- SECRET_KEY: Django secret
- DEBUG: false
- DATABASE_URL: e.g. postgres://USER:PASS@HOST:PORT/NAME
- STRIPE_SECRET_KEY: your Stripe secret key
- STRIPE_WEBHOOK_SECRET: your webhook signing secret
- EMAIL_BACKEND, EMAIL_HOST, EMAIL_PORT, EMAIL_HOST_USER, EMAIL_HOST_PASSWORD
- AWS_STORAGE_BUCKET_NAME, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY (if using S3)
- CELERY_BROKER_URL (e.g., redis://...), CELERY_RESULT_BACKEND

Quick checklist:
- Use HTTPS and set ALLOWED_HOSTS
- Use S3 or another cloud storage for media and configure `DEFAULT_FILE_STORAGE`
- Configure Redis + Celery for background tasks (notifications, emails)
- Configure Stripe webhooks and set STRIPE_WEBHOOK_SECRET in env
- Run collectstatic and migrations during deploy

Stripe local testing:
- Install Stripe CLI and authenticate: https://stripe.com/docs/stripe-cli
- Forward events to your local webhook: stripe listen --forward-to localhost:8000/api/payments/webhook/
- Trigger events: stripe trigger payment_intent.succeeded

Security tips:
- Enforce strong password validators
- Use TLS for all endpoints
- Add a WAF / rate limiting on auth endpoints
