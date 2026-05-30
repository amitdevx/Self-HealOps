from backend.core.security import get_password_hash, verify_password, create_access_token
import pytest

def test_password_hashing():
    password = "secretpassword"
    hashed = get_password_hash(password)
    assert hashed != password
    assert verify_password(password, hashed)
    assert not verify_password("wrongpassword", hashed)

def test_create_access_token():
    token = create_access_token(subject="user123")
    assert isinstance(token, str)
    assert len(token) > 20
