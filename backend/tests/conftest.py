import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, get_db
from app.models.user import User
from app.utils.jwt import create_access_token

# Test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture
def db_session():
    """Create test database"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(db_session):
    """Create test client"""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db_session):
    """Create test user"""
    from app.routers.auth import hash_password
    user = User(
        email="test@example.com",
        hashed_password=hash_password("testpass123"),
        is_paid=False
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_paid_user(db_session):
    """Create test paid user"""
    from app.routers.auth import hash_password
    user = User(
        email="paid@example.com",
        hashed_password=hash_password("testpass123"),
        is_paid=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def auth_token(test_user):
    """Create JWT token for test user"""
    return create_access_token(data={"sub": test_user.email})


@pytest.fixture
def paid_auth_token(test_paid_user):
    """Create JWT token for paid test user"""
    return create_access_token(data={"sub": test_paid_user.email})
