
# Trading Signals SaaS Prototype

This is a practical, end‑to‑end SaaS prototype for trading signals. It covers the core flow: signup/login with JWT, a ₹499 Stripe subscription, Redis caching + rate limits, and a simple React dashboard. The goal is to be demo‑ready and easy to run.

**Live demo:** [http://13.51.205.192/dashboard](http://13.51.205.192/dashboard)

## 🎯 What this demonstrates
- Email/password auth with JWT
- Free vs paid access (3 signals/day for free users)
- Stripe Checkout + idempotent webhooks
- Redis caching (5‑minute TTL)
- React dashboard with a clean flow

## 🧱 Tech Stack

**Backend**
- FastAPI
- SQLAlchemy (SQLite local / PostgreSQL prod)
- Redis (rate limit + cache + webhook idempotency)
- Stripe API
- Pytest

**Frontend**
- React 18 + React Router
- Axios (JWT interceptors)

## 🚀 Local Setup

### Prerequisites
- Python 3.10+
- Node.js 18+
- Docker & Docker Compose (recommended)

### Docker Compose

```bash
docker-compose up -d
docker-compose ps
```

**Services:**
- Redis: redis://localhost:6379
- PostgreSQL: postgresql://postgres:postgres@localhost:5432/trading_signals

**Backend:**
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
copy ..\env.docker .env
python -m uvicorn app.main:app --reload --port 8000
```

**Frontend:**
```bash
cd frontend
npm install
npm start
```

## 🔑 Environment Variables

**Backend .env**
```env
DATABASE_URL=sqlite:///./trading_signals.db
SECRET_KEY=your-secret-key-minimum-32-characters
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REDIS_URL=redis://localhost:6379
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
STRIPE_PRICE_ID=price_...
STRIPE_PUBLISHABLE_KEY=pk_test_...
FRONTEND_URL=http://localhost:3000
```

**Frontend .env.local**
```env
REACT_APP_API_URL=http://localhost:8000
REACT_APP_STRIPE_PUBLISHABLE_KEY=pk_test_...
```

## 🧪 Tests

```bash
cd backend
pytest tests/ -v
```

## 💳 Stripe Webhook Testing

```bash
# Install Stripe CLI: https://stripe.com/docs/stripe-cli
stripe login
stripe listen --forward-to localhost:8000/billing/webhook
stripe trigger checkout.session.completed
```

**Webhook events handled:**
- checkout.session.completed → activate subscription
- invoice.payment_succeeded → keep subscription active
- customer.subscription.deleted → downgrade to free

**Idempotency (Redis):**
```python
redis_key = f"stripe_event:{event_id}"
if redis.get(redis_key):
		return {"status": "already_processed"}
redis.setex(redis_key, 86400, "1")
```

## 🏗️ Architecture Diagram

```
React UI
	│ JWT
	▼
FastAPI Backend
	├─ Auth (JWT + Redis rate limit)
	├─ Billing (Stripe + webhooks)
	├─ Signals (Redis cache)
	└─ DB (Users/Subscriptions)
Redis
	├─ Rate limiting
	├─ Cache (TTL 5 min)
	└─ Webhook idempotency
Stripe
	└─ Checkout + Webhooks
```

## 🚀 Deployment (AWS EC2)

1. Provision an EC2 instance (Amazon Linux 2023) and open ports 80 and 8000
2. Install Python, Node.js, and Nginx
3. Clone repo and set backend env vars in backend/.env
4. Run backend with Gunicorn on port 8000
5. Build frontend and serve with Nginx (/usr/share/nginx/html)
6. Set Stripe webhook URL to http://<EC2_PUBLIC_IP>/billing/webhook

## ✅ Demo Flow

1. Signup/login
2. See free signals (3/day)
3. Subscribe via Stripe Checkout
4. Return to dashboard with paid status
5. Unlimited signals
