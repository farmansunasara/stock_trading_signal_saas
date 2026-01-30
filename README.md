# Trading Signals SaaS Prototype

A full-stack SaaS application for stock trading signals with JWT authentication, Stripe subscriptions (₹499), Redis caching, and a React dashboard. Built using FastAPI, SQLAlchemy, and React.

## 🎯 Overview

This prototype demonstrates a complete SaaS workflow:
- User signup/login with JWT authentication
- Free plan: 3 signals/day
- Paid plan: Unlimited signals via Stripe subscription (₹499)
- Real-time trading signals with Redis caching
- Idempotent webhook handling for payment events

## 🧱 Tech Stack

### Backend
- **FastAPI** - High-performance Python web framework
- **SQLAlchemy** - ORM with SQLite (local) / PostgreSQL (prod)
- **Redis** - Caching, rate limiting, webhook idempotency
- **JWT** - Token-based authentication (python-jose)
- **Stripe API** - Payment processing and subscriptions
- **Pytest** - Testing framework

### Frontend
- **React 18** - UI library with hooks
- **React Router** - Client-side routing
- **Axios** - HTTP client with interceptors
- **Context API** - State management for auth

### Infrastructure
- Railway / Render (backend deployment)
- Vercel / Netlify (frontend deployment)
- Environment-based configuration

## 📁 Project Structure

```
.
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application entry
│   │   ├── config.py            # Environment configuration
│   │   ├── database.py          # SQLAlchemy setup
│   │   ├── models/
│   │   │   └── user.py          # User model
│   │   ├── routers/
│   │   │   ├── auth.py          # Auth endpoints
│   │   │   ├── billing.py       # Stripe billing endpoints
│   │   │   └── signals.py       # Trading signals endpoints
│   │   ├── schemas/
│   │   │   ├── user.py          # Pydantic schemas
│   │   │   ├── billing.py
│   │   │   └── signal.py
│   │   └── utils/
│   │       ├── jwt.py           # JWT token handling
│   │       ├── redis_client.py  # Redis connection
│   │       └── stripe_client.py # Stripe configuration
│   ├── tests/
│   │   ├── conftest.py          # Pytest fixtures
│   │   ├── test_auth.py         # Auth tests
│   │   └── test_signals.py      # Signals tests
│   ├── requirements.txt
│   └── .env.example
│
├── frontend/
│   ├── src/
│   │   ├── App.js               # Main React component
│   │   ├── index.js             # Entry point
│   │   ├── pages/
│   │   │   ├── Login.js         # Login/signup page
│   │   │   └── Dashboard.js     # Signals dashboard
│   │   ├── services/
│   │   │   └── api.js           # Axios API client
│   │   ├── context/
│   │   │   └── AuthContext.js   # Auth state management
│   │   └── styles/              # CSS files
│   ├── public/
│   │   └── index.html
│   ├── package.json
│   └── .env.example
│
└── README.md
```

## 🚀 Local Setup

### Prerequisites
- Python 3.10+
- Node.js 18+
- Docker & Docker Compose (recommended for Redis + PostgreSQL)

### Option 1: Using Docker Compose (Recommended) 🐳

**Advantages:**
- ✅ Both Redis and PostgreSQL ready to go
- ✅ No manual installation needed
- ✅ Isolated environment
- ✅ Easy cleanup with `docker-compose down`

#### Start Services
```bash
# From project root
docker-compose up -d

# Verify services are running
docker-compose ps

# Check service health
docker-compose logs redis      # Redis logs
docker-compose logs postgres   # PostgreSQL logs
```

**Services Started:**
- Redis on `redis://localhost:6379`
- PostgreSQL on `postgresql://postgres:postgres@localhost:5432/trading_signals`

#### Setup Backend
```bash
cd backend

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Use Docker environment file
copy ..\env.docker .env

# Run migrations (if using PostgreSQL in production)
# For local SQLite: leave DATABASE_URL as is

# Start backend
python -m uvicorn app.main:app --reload --port 8000
```

#### Setup Frontend
```bash
cd frontend
npm install
npm start  # Runs on port 3000
```

#### Stop Services
```bash
docker-compose down -v  # -v removes volumes
```

---

### Option 2: Manual Setup (Local Redis)

#### Start Redis
Using Docker:
```bash
docker run -d --name redis -p 6379:6379 redis:7-alpine
```

Or use local Redis installation on port 6379.

### 3. Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Configure environment
copy .env.example .env
# Edit .env and add your Stripe keys

# Run server
uvicorn app.main:app --reload --port 8000
```

Backend will be available at `http://localhost:8000`

### 4. Frontend Setup
Open a new terminal:
```bash
cd frontend

# Install dependencies
npm install

# Configure environment
copy .env.example .env.local
# Edit .env.local if needed

# Start development server
npm start
```

Frontend will be available at `http://localhost:3000`

## 🔑 Environment Variables

### Backend `.env`
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

### Frontend `.env.local`
```env
REACT_APP_API_URL=http://localhost:8000
REACT_APP_STRIPE_PUBLISHABLE_KEY=pk_test_...
```

## 🧪 Running Tests

```bash
cd backend
pytest tests/ -v --cov=app
```

### Test Coverage (19 tests)

**Authentication Tests (3)**
- ✅ `test_signup_login` - JWT token generation
- ✅ `test_auth_protected_route` - 401 without auth
- ✅ `test_auth_me_with_valid_token` - Get user info

**Billing Tests (13)**
- ✅ `test_create_checkout_session` - Stripe checkout creation
- ✅ `test_create_checkout_session_existing_customer` - Existing customer flow
- ✅ `test_create_checkout_session_without_auth` - Auth required
- ✅ `test_get_billing_status_free_user` - Free user status
- ✅ `test_get_billing_status_paid_user` - Paid user status
- ✅ `test_webhook_checkout_completed` - Payment success handling
- ✅ `test_webhook_invoice_payment_succeeded` - Subscription renewal
- ✅ `test_webhook_subscription_deleted` - Cancellation handling
- ✅ `test_webhook_idempotency` - **Prevent duplicate processing**
- ✅ `test_webhook_invalid_signature` - Signature verification
- ✅ `test_webhook_invalid_payload` - Payload validation
- ✅ `test_webhook_unknown_event_type` - Graceful handling
- ✅ `test_stripe_error_handling` - Error scenarios

**Signals Tests (3)**
- ✅ `test_signals_free_user` - Rate limiting (3/day)
- ✅ `test_signals_paid_user` - Unlimited access
- ✅ `test_signals_without_auth` - Auth required

## 💳 Stripe Webhook Testing

### Using Stripe CLI
```bash
# Install Stripe CLI: https://stripe.com/docs/stripe-cli

# Login to Stripe
stripe login

# Forward webhooks to local backend
stripe listen --forward-to localhost:8000/billing/webhook

# Test checkout flow
stripe trigger checkout.session.completed
```

The webhook endpoint at `/billing/webhook` handles:
- `checkout.session.completed` → Activate subscription
- `invoice.payment_succeeded` → Extend subscription
- `customer.subscription.deleted` → Downgrade to free

### Idempotency Implementation
Redis stores webhook event IDs for 24 hours to prevent duplicate processing:
```python
redis_key = f"stripe_event:{event_id}"
if redis.get(redis_key):
    return {"status": "already_processed"}
redis.setex(redis_key, 86400, "1")  # 24h TTL
```

## 🏗️ System Architecture

```
┌─────────────────┐
│   React UI      │
│  (Port 3000)    │
└────────┬────────┘
         │ JWT Token
         ▼
┌─────────────────────────────────┐
│      FastAPI Backend            │
│       (Port 8000)               │
├─────────────────────────────────┤
│  ┌──────────────────────────┐  │
│  │  Auth Module             │  │
│  │  - JWT tokens            │  │
│  │  - Rate limiting (Redis) │  │
│  └──────────────────────────┘  │
│  ┌──────────────────────────┐  │
│  │  Billing Module          │  │
│  │  - Stripe Checkout       │  │
│  │  - Webhook idempotency   │  │
│  └──────────────────────────┘  │
│  ┌──────────────────────────┐  │
│  │  Signals Module          │  │
│  │  - Redis caching (5min)  │  │
│  │  - Rate limits (free)    │  │
│  └──────────────────────────┘  │
└──────────┬───────────┬──────────┘
           │           │
    ┌──────▼────┐  ┌──▼─────────┐
    │   SQLite  │  │   Redis    │
    │  (Users)  │  │  (Cache)   │
    └───────────┘  └────────────┘
                   
    ┌──────────────┐
    │   Stripe     │
    │  Webhooks    │
    └──────────────┘
```

## 📋 Demo Flow

1. **Signup**: Navigate to `http://localhost:3000` → Sign up with email/password
2. **Free Access**: View dashboard with 3 free signals (rate limited)
3. **Try Exceeding Limit**: Refresh signals 4 times → See "Daily limit exceeded" error
4. **Subscribe**: Click "Subscribe for ₹499" → Redirected to Stripe Checkout
5. **Payment**: Use test card `4242 4242 4242 4242` (any future expiry/CVC)
6. **Success**: Redirected back to dashboard with "Paid Plan" badge
7. **Unlimited Access**: Refresh signals multiple times → No rate limit

## 🔍 Key Features Implemented

### 1. Authentication & Rate Limiting
- Bcrypt password hashing
- JWT tokens with 30-min expiry
- Redis-based rate limiting (10 req/min per IP)

### 2. Stripe Integration
- Checkout Session creation with metadata
- Webhook signature verification
- Idempotent event processing (prevents duplicate payments)
- Automatic user status updates

### 3. Trading Signals
- Mock signal generation (NIFTY/BANKNIFTY)
- Redis caching with 5-minute TTL
- Free users: 3 signals/day (Redis counter)
- Paid users: Unlimited access

### 4. Frontend
- Context API for auth state
- Axios interceptors for JWT injection
- Loading and error states
- Responsive design with clean CSS

## 🚀 Deployment

### Docker-Based Local Development

**Complete Stack:**
```bash
# Start everything
docker-compose up -d

# Access services:
# - Backend:   http://localhost:8000
# - Frontend:  http://localhost:3000
# - Redis:     redis://localhost:6379
# - Postgres:  postgresql://postgres:postgres@localhost:5432/trading_signals

# View logs
docker-compose logs -f backend   # Backend logs
docker-compose logs -f redis     # Redis logs

# Stop everything
docker-compose down
```

---

### Cloud Deployment

#### Backend (Railway / Render)
1. Push code to GitHub
2. Connect repository to Railway/Render
3. Add environment variables:
   - `DATABASE_URL=postgresql://...`
   - `REDIS_URL=redis://...`
   - Stripe keys
4. Deploy and note the backend URL

**Railway Setup Example:**
```bash
# 1. Install Railway CLI
npm i -g @railway/cli

# 2. Login
railway login

# 3. Initialize project
railway init

# 4. Link to GitHub
# 5. Add PostgreSQL & Redis from Railway dashboard
# 6. Deploy
railway up
```

### Frontend (Vercel / Netlify)
1. Push code to GitHub
2. Connect repository to Vercel/Netlify
3. Set `REACT_APP_API_URL` to your backend URL
4. Deploy

### Post-Deployment
1. Update Stripe webhook endpoint to production URL
2. Test complete flow in production
3. Monitor webhook logs in Stripe dashboard

## 📊 API Endpoints

### Authentication
- `POST /auth/signup` - Create new user account
- `POST /auth/login` - Login and receive JWT token
- `GET /auth/me` - Get current user info (requires auth)

### Billing
- `POST /billing/create-checkout` - Create Stripe checkout session
- `GET /billing/status` - Get subscription status
- `POST /billing/webhook` - Stripe webhook handler

### Signals
- `GET /signals` - Get trading signals (cached, rate limited)

### Health
- `GET /` - API info
- `GET /health` - Health check

## 🐛 Troubleshooting

**Redis connection error**: Ensure Redis is running on port 6379
```bash
redis-cli ping  # Should return PONG
```

**Stripe webhook signature error**: Verify `STRIPE_WEBHOOK_SECRET` matches Stripe CLI output

**CORS error**: Check that `FRONTEND_URL` in backend `.env` matches your frontend URL

**Rate limit not working**: Flush Redis cache
```bash
redis-cli FLUSHALL
```

## 📝 Development Notes

- SQLite is used locally for simplicity (no setup required)
- Signals are mocked - replace with real ML model in production
- Frontend uses basic CSS - can be upgraded to Tailwind/MUI
- Tests cover core functionality - expand as needed

## 🎥 Video Demo

Record a 3-minute demo showing:
1. Signup/Login flow
2. Free plan limitations (3 signals)
3. Subscription via Stripe
4. Paid plan unlimited access

---

**Built as a practical interview task for Hashtechy - demonstrating end-to-end SaaS implementation with payment integration.**
