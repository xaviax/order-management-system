# Order Management System (APIs)

A Django REST Framework project for managing menu items, carts, orders, and user roles (Customers, Managers, Delivery Crew).
The API demonstrates role-based access control, JWT authentication (Djoser + SimpleJWT), filtering, searching, ordering, pagination and throttling.

##  Features

- JWT Authentication with Djoser & SimpleJWT
- Role-based permissions (Customer / Manager / Delivery Crew)
- Menu items CRUD (Manager-only writes)
- Cart → Order flow (customers place orders from their cart)
- Managers assign Delivery Crew to orders
- Delivery Crew update order delivery status
- Filtering, searching, ordering and pagination for list endpoints
- Rate limiting (throttling) for anonymous and authenticated users
- Uses MySQL (configurable) in settings.py

## 🛠 Requirements

- Python 3.10+ (project uses Django 5+)
- MySQL server (or change DB engine to SQLite for quick testing)
- pip / virtual environment

Typical dependencies (example in requirements.txt):

```
Django>=5.0
djangorestframework
djoser
djangorestframework-simplejwt
django-filter
mysqlclient          # or pymysql alternative
```

### Installation

Install dependencies:

```bash
python -m venv venv
# Linux/macOS
source venv/bin/activate
# Windows (PowerShell)
venv\Scripts\Activate.ps1

pip install -r requirements.txt
```

If using MySQL, install the driver:

```bash
pip install mysqlclient
# On Windows you may need build tools; alternative: pip install pymysql and configure accordingly.
```

## ⚙️ Configuration (quick)

Edit `settings.py` and set your DB credentials:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'order_management_db',
        'USER': 'your_mysql_user',
        'PASSWORD': 'your_mysql_password',
        'HOST': '127.0.0.1',
        'PORT': '3306',
        'OPTIONS': {
            "init_command": "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}
```

JWT sample config (already present in project):

```python
from datetime import timedelta

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=30),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
    "AUTH_HEADER_TYPES": ("Bearer",),
}
```

DRF defaults (pagination / filters / throttling):

```python
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 5,
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ],
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": "10/minute",
        "user": "30/minute",
    },
}
```

## ⚡ Database setup & run

Make migrations and migrate:

```bash
python manage.py makemigrations
python manage.py migrate
```

Create superuser (admin):

```bash
python manage.py createsuperuser
```

Start the dev server:

```bash
python manage.py runserver
```

Admin panel: http://127.0.0.1:8000/admin/ — create groups and assign users:

- Manager
- Customer
- Delivery Crew

**Note:** If you previously used SQLite then switched to MySQL, existing data will not automatically move. Use `dumpdata/loaddata` if you want to copy data.

## 🔐 Authentication endpoints

- `POST /auth/jwt/create/` — obtain access/refresh JWT (send username and password)
- `POST /auth/jwt/refresh/` — refresh access token
- `POST /auth/users/` — register (Djoser default signup)

All protected endpoints use `Authorization: Bearer <ACCESS_TOKEN>`.

## 📦 API endpoints (summary)

### Menu Items

- `GET /api/menu-items/` — list (supports pagination, filtering, search, ordering)
- `POST /api/menu-items/` — create (Manager only)
- `GET /api/menu-items/<id>/` — retrieve
- `PUT/PATCH /api/menu-items/<id>/` — update (Manager only)
- `DELETE /api/menu-items/<id>/` — delete (Manager only)

### Group Management (Manager-only)

- `GET /api/groups/manager/users/` — list managers
- `POST /api/groups/manager/users/` — assign user to Manager (provide `{"username": "..."}`)
- `DELETE /api/groups/manager/users/<id>/` — remove user from Manager
- `GET /api/groups/delivery-crew/users/` — list delivery crew
- `POST /api/groups/delivery-crew/users/` — assign user to Delivery Crew (provide `{"username": "..."}`)
- `DELETE /api/groups/delivery-crew/users/<id>/` — remove user from Delivery Crew

### Cart (Customer-only)

- `GET /api/cart/menu-items/` — list cart items for authenticated user
- `POST /api/cart/menu-items/` — add to cart (send `{"menuitem": <id>, "quantity": <n>}`) — server calculates unit_price and price
- `DELETE /api/cart/menu-items/` — empty the authenticated user's cart

### Orders

- `GET /api/orders/` — list orders (Customer sees own; Manager sees all; Delivery Crew sees assigned)
- `POST /api/orders/` — create order from current user's cart (no body required)
- `GET /api/orders/<id>/` — retrieve a specific order (access limited by role)
- `PUT/PATCH /api/orders/<id>/` — update:
  - **Manager:** assign delivery_crew (send `{"delivery_crew": <user_id>}`)
  - **Delivery Crew:** update status (send `{"status": true}` or `{"status": 1}`)
- `DELETE /api/orders/<id>/` — delete an order (Manager only)

##  Filtering, Searching, Ordering & Pagination

- **Pagination:** default page size is 5. Use `?page=2`.
- **Search:** `?search=<term>` (menu items by title)
- **Ordering:** `?ordering=price` or `?ordering=-price`
- **Filtering:** field filters, e.g.:
  - Menu items: `?category=<id>&price=<value>`
  - Orders: `?status=true&date=2025-09-01&ordering=-total`

##  Notes on behavior & implementation details

- When adding to cart, only `menuitem` and `quantity` are provided by the client; the server looks up `MenuItem.price` and stores `unit_price` and `price` in `Cart`.

- On order creation (`POST /api/orders/`), the server:
  - reads the authenticated user's Cart rows,
  - computes total,
  - creates Order and OrderItem rows (snapshots unit_price/price),
  - empties the user's cart — wrapped in a DB transaction to ensure atomicity.

- Managers assign `delivery_crew` via order update; Delivery Crew update `status` only. Views enforce role-based field restrictions during updates.

- Throttling is applied globally; you can override per-view using `throttle_classes`.


