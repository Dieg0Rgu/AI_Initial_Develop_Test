from __future__ import annotations
import tempfile
from pathlib import Path
from fastapi.testclient import TestClient
from app.services.auth_service import AuthService
from app.main import app

client = TestClient(app)


def test_auth_service_sqlite_initialization():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test_auth.db"
        service = AuthService(db_path=db_path)

        # Should seed default admin
        admin_auth = service.authenticate("admin", "admin123")
        assert admin_auth is not None
        assert admin_auth["user"]["username"] == "admin"
        assert admin_auth["user"]["role"] == "admin"
        assert "token" in admin_auth

        # Invalid password should fail
        assert service.authenticate("admin", "wrong_password") is None
        # Non-existent user should fail
        assert service.authenticate("non_existent", "admin123") is None


def test_auth_service_registration_and_tokens():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test_auth.db"
        service = AuthService(db_path=db_path)

        # Register new user
        reg_res = service.register(
            email="chef@gastroteacher.com",
            username="chef_maria",
            password="securePassword123",
            full_name="María Chef",
            role="viewer"
        )
        assert reg_res["user"]["email"] == "chef@gastroteacher.com"
        assert reg_res["user"]["username"] == "chef_maria"
        assert "token" in reg_res

        # Verify token
        payload = service.verify_token(reg_res["token"])
        assert payload is not None
        assert payload["email"] == "chef@gastroteacher.com"

        # Duplicate email should raise ValueError
        try:
            service.register(
                email="chef@gastroteacher.com",
                username="another_user",
                password="password123",
                full_name="Another"
            )
            assert False, "Expected ValueError for duplicate email"
        except ValueError as e:
            assert "ya está registrado" in str(e)

        # Duplicate username should raise ValueError
        try:
            service.register(
                email="unique@gastroteacher.com",
                username="chef_maria",
                password="password123",
                full_name="Another"
            )
            assert False, "Expected ValueError for duplicate username"
        except ValueError as e:
            assert "ya está en uso" in str(e)


def test_auth_endpoints_api():
    # 1. Login with seeded admin
    login_res = client.post("/api/auth/login", json={
        "username_or_email": "admin",
        "password": "admin123"
    })
    assert login_res.status_code == 200
    token = login_res.json()["token"]

    # 2. Access /api/auth/me with Bearer token
    me_res = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_res.status_code == 200
    assert me_res.json()["user"]["username"] == "admin"

    # 3. Access without token should return 401
    bad_me = client.get("/api/auth/me")
    assert bad_me.status_code == 401

    # 4. Access with invalid token should return 401
    bad_token_me = client.get("/api/auth/me", headers={"Authorization": "Bearer invalid.token"})
    assert bad_token_me.status_code == 401

    # 5. Register via API
    import uuid
    unique_user = f"tester_{uuid.uuid4().hex[:8]}"
    reg_api = client.post("/api/auth/register", json={
        "email": f"{unique_user}@test.com",
        "username": unique_user,
        "password": "testPassword123",
        "full_name": "API Tester"
    })
    assert reg_api.status_code == 200
    assert reg_api.json()["status"] == "success"
