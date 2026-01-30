import pytest


def test_signals_free_user(client, auth_token):
    """Test signals endpoint for free user - verify rate limit enforced"""
    
    # First 3 requests should succeed
    for i in range(3):
        response = client.get(
            "/signals",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["is_paid"] == False
        assert len(data["signals"]) == 3  # Free users get limited signals
        assert "3/day" in data["user_limit"]
    
    # 4th request should fail with 403
    response = client.get(
        "/signals",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 403
    assert "Daily limit exceeded" in response.json()["detail"]


def test_signals_paid_user(client, paid_auth_token):
    """Test signals endpoint for paid user - verify unlimited access"""
    
    # Paid users should get unlimited signals
    for i in range(10):  # Test multiple requests
        response = client.get(
            "/signals",
            headers={"Authorization": f"Bearer {paid_auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["is_paid"] == True
        assert len(data["signals"]) > 3  # Paid users get all signals
        assert data["user_limit"] is None


def test_signals_without_auth(client):
    """Test signals endpoint without authentication"""
    response = client.get("/signals")
    assert response.status_code == 403  # No authorization header
