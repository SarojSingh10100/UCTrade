# Example responses (uctrade API)

## Register (POST /api/users/register/)
Request body:
{
  "username": "testuser",
  "email": "test@example.com",
  "password": "StrongPassw0rd!",
  "password2": "StrongPassw0rd!"
}

Response 201 Created:
{
  "id": 1,
  "username": "testuser",
  "email": "test@example.com",
  "is_instructor": false
}

## Token (POST /api/token/)
Request body:
{
  "username": "testuser",
  "password": "StrongPassw0rd!"
}

Response 200 OK:
{
  "refresh": "<refresh_token>",
  "access": "<access_token>"
}

## Create Course (POST /api/courses/)
Headers: Authorization: Bearer <access_token>

Request body:
{
  "title": "Intro to Django",
  "description": "Course description",
  "price": "29.99"
}

Response 201 Created:
{
  "id": 1,
  "title": "Intro to Django",
  "slug": "intro-to-django",
  "description": "Course description",
  "price": "29.99",
  "instructor": "inst",
  "created_at": "2025-01-01T00:00:00Z"
}

## Add to Cart (POST /api/cart/)
Headers: Authorization: Bearer <access_token>

Request body:
{
  "course": 1
}

Response 201 Created:
{
  "id": 1,
  "course": 1,
  "quantity": 1
}

## Create PaymentIntent (POST /api/payments/create-intent/)
Headers: Authorization: Bearer <access_token>

Request body:
{ "order_id": 1 }

Response 200 OK:
{ "client_secret": "pi_..._secret_..." }
