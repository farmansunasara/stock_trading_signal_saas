# 🔥 AGENT INSTRUCTION — PRACTICAL INTERVIEW MODE

## Role
You are a **Senior Full-Stack Engineer (FastAPI + React)** executing a time-bound interview practical.  
Your goal: **Deliver a working SaaS prototype, not over-engineer.**

## Constraints
- **Deadline**: 48 hours
- Focus on **core flow working + clean code**
- Prefer **clarity > perfection**
- Use **mocks where allowed**
- Everything must be **demo-ready**

---

## 🎯 OBJECTIVE
Build a **Trading Signals SaaS Prototype** with:
- ✅ Auth (JWT)
- ✅ Stripe subscription (₹499)
- ✅ Redis caching + idempotent webhooks
- ✅ Paid vs free signal access
- ✅ React dashboard
- ✅ Deployed backend + frontend
- ✅ Clean README + short demo flow

---

## 🧱 TECH STACK (STRICT)

### Backend
- FastAPI
- SQLAlchemy
- SQLite (local) / PostgreSQL (prod)
- Redis (cache + rate limit + webhook idempotency)
- JWT auth (python-jose or pyjwt)
- Stripe API
- Pytest

### Frontend
- React (Vite or CRA)
- REST API only (NO GraphQL)
- JWT stored in memory/localStorage
- Axios for HTTP

### Infra
- Deploy on Railway / Render / EC2
- Env-based config
- Docker optional (bonus, not required)

---

## 🧩 SYSTEM ARCHITECTURE (EXPECTED)

```
React UI
   ↓ JWT
FastAPI Backend
   ├── Auth (JWT + Rate limit via Redis)
   ├── Billing (Stripe Checkout + Webhooks)
   ├── Signals API (Redis cached)
   └── DB (Users, Subscriptions)
Redis
   ├── Rate limiting
   ├── Signal caching (TTL 5 min)
   └── Webhook idempotency
Stripe
   └── Checkout + Webhooks
```

---

## 🛠️ IMPLEMENTATION TASKS

### 1️⃣ AUTH MODULE
**Goal**: Email + password signup/login with JWT

**Requirements**:
- Password hashing (bcrypt/passlib)
- JWT access token (30 min expiry)
- Redis rate-limit on login/signup (10 req/min per IP)

**Endpoints**:
```
POST /auth/signup
POST /auth/login
GET  /auth/me
```

**Database Schema**:
```python
class User(Base):
    id: int
    email: str (unique, indexed)
    hashed_password: str
    is_paid: bool (default=False)
    stripe_customer_id: str (nullable)
    created_at: datetime
```

---

### 2️⃣ STRIPE BILLING
**Goal**: ₹499 subscription via Stripe Checkout

**Requirements**:
- Create Stripe Checkout Session (one-time payment or subscription)
- On success → set `user.is_paid = True`
- Stripe webhook handler with **Redis idempotency**

**Endpoints**:
```
POST /billing/create-checkout
GET  /billing/status
POST /billing/webhook
```

**Critical Logic**:
```python
# Redis idempotency check
redis_key = f"stripe_event:{event_id}"
if redis.get(redis_key):
    return {"status": "already_processed"}
redis.setex(redis_key, 86400, "1")  # 24h TTL

# Map Stripe customer → User
user = db.query(User).filter_by(stripe_customer_id=customer_id).first()
user.is_paid = True
db.commit()
```

**Webhook Events to Handle**:
- `checkout.session.completed` → Activate subscription
- `invoice.payment_succeeded` → Extend subscription
- `customer.subscription.deleted` → Downgrade to free

---

### 3️⃣ SIGNALS MODULE
**Goal**: Mock trading signals with Redis caching

**Requirements**:
- Mock signals for NIFTY/BANKNIFTY (simulate expensive computation)
- Cache result in Redis (TTL = 300 sec)
- Free user → 3 signals/day (Redis rate limit)
- Paid user → unlimited signals

**Endpoint**:
```
GET /signals
Headers: Authorization: Bearer <JWT>
```

**Response Example**:
```json
{
  "signals": [
    {
      "symbol": "NIFTY",
      "type": "BUY",
      "price": 21500,
      "confidence": 0.85,
      "timestamp": "2026-01-30T10:00:00Z"
    }
  ],
  "user_limit": "3/day (upgrade for unlimited)"
}
```

**Redis Caching Logic**:
```python
cache_key = f"signals:{symbol}:{date}"
cached = redis.get(cache_key)
if cached:
    return json.loads(cached)

# Generate signals (mock)
signals = generate_mock_signals()
redis.setex(cache_key, 300, json.dumps(signals))
return signals
```

**Rate Limiting Logic**:
```python
if not user.is_paid:
    rate_key = f"signal_limit:{user.id}:{date}"
    count = redis.incr(rate_key)
    redis.expire(rate_key, 86400)  # Reset daily
    if count > 3:
        raise HTTPException(403, "Daily limit exceeded")
```

---

### 4️⃣ REACT FRONTEND

**Pages**:
- `/login` - Email/password form
- `/dashboard` - Signals table + subscription status

**Dashboard Requirements**:
- Show signals in a table
- Display subscription status (Free / Paid)
- "Subscribe for ₹499" button → Stripe Checkout redirect
- Handle loading + error states

**Auth Flow**:
```javascript
// Store JWT in memory or localStorage
localStorage.setItem('token', response.data.access_token);

// Axios interceptor
axios.interceptors.request.use(config => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});
```

**Frontend Rules**:
- No UI libraries required (basic CSS OK)
- Clean separation: `/services/api.js` for API calls
- Context API for auth state (optional)

---

### 5️⃣ TESTING (MINIMUM)

**Write Pytest tests for**:
1. `test_signup_login` - Verify JWT returned
2. `test_auth_protected_route` - Verify 401 without JWT
3. `test_signals_free_user` - Verify rate limit enforced
4. `test_signals_paid_user` - Verify unlimited access

**Example Test**:
```python
def test_signals_free_user(client, db_session):
    user = create_user(is_paid=False)
    token = create_jwt(user)
    
    # First 3 requests succeed
    for _ in range(3):
        response = client.get("/signals", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200
    
    # 4th request fails
    response = client.get("/signals", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 403
```

---

### 6️⃣ DEPLOYMENT

**Backend**:
- Deploy on Railway / Render with:
  - PostgreSQL (or keep SQLite)
  - Redis instance
  - Stripe secrets in env vars

**Frontend**:
- Deploy on Vercel / Netlify
- Set `REACT_APP_API_URL` to backend URL

**Env Vars**:
```bash
# Backend
DATABASE_URL=postgresql://...
REDIS_URL=redis://...
SECRET_KEY=your-jwt-secret
STRIPE_SECRET_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...
STRIPE_PRICE_ID=price_...

# Frontend
REACT_APP_API_URL=https://backend.railway.app
REACT_APP_STRIPE_PUBLISHABLE_KEY=pk_live_...
```

---

## 📄 README REQUIREMENTS (MANDATORY)

**Must Include**:
1. **Project Overview** - One paragraph description
2. **Tech Stack** - Bullet points
3. **Local Setup** - Commands for backend + frontend + Redis
4. **Stripe Webhook Testing** - Using Stripe CLI
5. **Architecture Diagram** - ASCII art or image
6. **Demo Flow** - Step-by-step user journey

**Example Local Setup**:
```bash
# Backend
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload

# Redis
docker run -d -p 6379:6379 redis

# Frontend
cd frontend
npm install
npm start
```

---

## 🎥 DEMO VIDEO (3 MIN MAX)

**Show**:
1. Signup + Login
2. Dashboard (free signals, rate limited)
3. Click "Subscribe" → Stripe checkout
4. Payment success → unlimited signals unlocked

---

## 🚨 EVALUATION PRIORITY (OPTIMIZE FOR THIS)

✅ **End-to-end flow works** (auth → dashboard → payment → signals)  
✅ **Stripe webhook idempotency** (no duplicate activations)  
✅ **Redis caching logic** (signals cached for 5 min)  
✅ **Clean API structure** (proper separation of concerns)  
✅ **Clear README + demo** (someone can run this in 5 min)

❌ **Avoid**:
- Over-engineering (no microservices, no Kubernetes)
- Fancy UI (basic CSS is fine)
- Extra features not asked (email notifications, analytics, etc.)

---

## 🧠 MINDSET

> **This is not a tutorial project. This is "can you ship?" test.**

**Ship fast. Ship clean. Ship working.**

- Use mocks instead of real ML models
- Hardcode signals if needed
- Focus on plumbing (auth → payment → access control)
- Write minimal tests that prove core logic works
- Deploy early, iterate fast

**Key Success Metrics**:
1. Can a user signup, pay, and see paid signals? ✅
2. Are webhooks idempotent? ✅
3. Is Redis used correctly? ✅
4. Can someone run this locally in < 10 min? ✅

**Time Allocation** (48h):
- Auth + DB setup: 4h
- Stripe integration: 6h
- Signals API + Redis: 4h
- Frontend: 8h
- Testing: 4h
- Deployment: 6h
- README + Demo: 2h
- Buffer: 14h
