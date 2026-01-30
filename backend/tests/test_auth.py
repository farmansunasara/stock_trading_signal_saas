def test_signup_login(client):
    """Test user signup and login - verify JWT returned"""
    
    # Test signup
    signup_data = {
        "email": "newuser@example.com",
        "password": "password123"
    }
    response = client.post("/auth/signup", json=signup_data)
    assert response.status_code == 201
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"
    
    # Test login with same credentials
    login_data = {
        "email": "newuser@example.com",
        "password": "password123"
    }
    response = client.post("/auth/login", json=login_data)
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"


def test_auth_protected_route(client, test_user):
    """Test that protected routes return 401 without JWT"""
    
    # Try to access /auth/me without token
    response = client.get("/auth/me")
    assert response.status_code == 403  # Missing authorization header
    
    # Try with invalid token
    response = client.get(
        "/auth/me",
        headers={"Authorization": "Bearer invalid_token"}
    )
    assert response.status_code == 401


def test_auth_me_with_valid_token(client, auth_token, test_user):
    """Test /auth/me endpoint with valid token"""
    response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == test_user.email
    assert data["is_paid"] == False
