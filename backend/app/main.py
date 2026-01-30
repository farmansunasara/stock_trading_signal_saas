from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base
from .models import user
from .auth import router as auth
from .billing import router as billing
from .signals import router as signals
from .config import settings

# Create database tables
Base.metadata.create_all(bind=engine)

# Create FastAPI app
app = FastAPI(
    title="Trading Signals SaaS API",
    description="FastAPI backend for stock trading signals with Stripe subscriptions",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL, "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(billing.router)
app.include_router(signals.router)


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "online",
        "message": "Trading Signals SaaS API",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """Health check for deployment"""
    return {"status": "healthy"}
