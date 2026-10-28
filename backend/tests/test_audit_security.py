import pytest
from app.core.security import get_password_hash, verify_password
from app.models.audit_log import sanitize_audit_payload


def test_password_hashing_and_verification():
    """Verify password hashing produces salted hashes and verifies cleanly."""
    plain = "SecureCommandPass2026!"
    hashed = get_password_hash(plain)

    assert hashed != plain
    assert len(hashed) > 20
    assert verify_password(plain, hashed) is True
    assert verify_password("WrongPassword!", hashed) is False
    assert verify_password("", hashed) is False


def test_audit_log_sensitive_payload_sanitization():
    """Verify audit log payload sanitizer redacts confidential authentication data."""
    raw_payload = {
        "username": "command_admin",
        "action": "LOGIN",
        "password": "ClearTextPassword123!",
        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        "api_secret": "my-ultra-secret-key",
        "nested_details": {
            "refresh_token": "token_refresh_abc",
            "safe_field": "disaster_zone_01",
        },
        "safe_list": ["zone-01", "zone-02"],
    }

    sanitized = sanitize_audit_payload(raw_payload)

    assert sanitized["username"] == "command_admin"
    assert sanitized["password"] == "[REDACTED_SECURITY_DATA]"
    assert sanitized["access_token"] == "[REDACTED_SECURITY_DATA]"
    assert sanitized["api_secret"] == "[REDACTED_SECURITY_DATA]"
    assert sanitized["nested_details"]["refresh_token"] == "[REDACTED_SECURITY_DATA]"
    assert sanitized["nested_details"]["safe_field"] == "disaster_zone_01"
    assert sanitized["safe_list"] == ["zone-01", "zone-02"]
