"""Tests for security utilities."""
import pytest
from jose import jwt
from datetime import timedelta

from backend.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    ALGORITHM,
)
from backend.core.config import settings


def test_password_hashing():
    """Test password hashing and verification."""
    password = "secretpassword123"
    hashed = get_password_hash(password)
    assert hashed != password
    assert verify_password(password, hashed)
    assert not verify_password("wrongpassword", hashed)


def test_password_hash_uniqueness():
    """Test that same password produces different hashes (bcrypt salt)."""
    password = "samepassword"
    hash1 = get_password_hash(password)
    hash2 = get_password_hash(password)
    assert hash1 != hash2
    assert verify_password(password, hash1)
    assert verify_password(password, hash2)


def test_create_access_token():
    """Test JWT access token creation."""
    token = create_access_token(subject="user-123")
    assert isinstance(token, str)
    assert len(token) > 20
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
    assert payload["sub"] == "user-123"
    assert payload["type"] == "access"
    assert "exp" in payload


def test_create_access_token_custom_expiry():
    """Test token with custom expiry delta."""
    token = create_access_token(
        subject="user-456", expires_delta=timedelta(minutes=5)
    )
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
    assert payload["sub"] == "user-456"


def test_create_refresh_token():
    """Test JWT refresh token creation."""
    token = create_refresh_token(subject="user-789")
    assert isinstance(token, str)
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
    assert payload["sub"] == "user-789"
    assert payload["type"] == "refresh"


def test_invalid_password_verification():
    """Test that verification fails with empty/None."""
    hashed = get_password_hash("validpassword")
    assert not verify_password("", hashed)
