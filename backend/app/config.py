from pydantic_settings import BaseSettings
from pydantic import validator
from typing import Optional
import os


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "sqlite:///./trading_signals.db"
    
    # JWT
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    # Stripe
    STRIPE_SECRET_KEY: str
    STRIPE_WEBHOOK_SECRET: str
    STRIPE_PRICE_ID: str
    STRIPE_PUBLISHABLE_KEY: str
    
    # CORS
    FRONTEND_URL: str = "http://localhost:3000"
    
    # Environment
    DEBUG: bool = False
    ENVIRONMENT: str = "development"
    ALLOWED_HOSTS: str = "localhost,127.0.0.1"
    
    class Config:
        env_file = ".env"
    
    @validator('SECRET_KEY')
    def validate_secret_key_length(cls, v):
        """Ensure SECRET_KEY is long enough"""
        if len(v) < 32:
            raise ValueError('SECRET_KEY must be at least 32 characters')
        return v


settings = Settings()
