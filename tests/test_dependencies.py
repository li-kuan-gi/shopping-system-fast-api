import pytest
import jwt
import json
import base64
from collections.abc import Mapping
from unittest.mock import MagicMock
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from cryptography.hazmat.primitives.asymmetric import ec
from src.dependencies import get_current_user


def bytes_to_base64url(b: bytes) -> str:
    return base64.urlsafe_b64encode(b).decode("utf-8").replace("=", "")


@pytest.fixture(scope="session")
def test_key_pair() -> tuple[ec.EllipticCurvePrivateKey, Mapping[str, object]]:
    """Generates a stable EC key pair for the test session."""
    private_key = ec.generate_private_key(ec.SECP256R1())
    public_key = private_key.public_key()

    # Get coordinates for JWK
    numbers = public_key.public_numbers()
    x = numbers.x.to_bytes(32, "big")
    y = numbers.y.to_bytes(32, "big")

    jwk = {
        "kty": "EC",
        "crv": "P-256",
        "x": bytes_to_base64url(x),
        "y": bytes_to_base64url(y),
        "alg": "ES256",
        "use": "sig",
    }

    return private_key, jwk


@pytest.fixture
def mock_env_signing_key(
    monkeypatch: pytest.MonkeyPatch,
    test_key_pair: tuple[ec.EllipticCurvePrivateKey, Mapping[str, object]],
) -> None:
    _, jwk = test_key_pair
    monkeypatch.setenv("SUPABASE_JWT_SIGNING_KEY", json.dumps(jwk))


@pytest.mark.usefixtures("mock_env_signing_key")
def test_get_current_user_success(
    test_key_pair: tuple[ec.EllipticCurvePrivateKey, Mapping[str, object]],
) -> None:
    private_key, _ = test_key_pair
    payload = {"sub": "123", "email": "test@example.com", "aud": "authenticated"}
    token = jwt.encode(payload, private_key, algorithm="ES256")

    auth = MagicMock(spec=HTTPAuthorizationCredentials)
    auth.credentials = token

    user = get_current_user(auth)

    assert user.id == "123"


def test_get_current_user_missing_secret(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("SUPABASE_JWT_SIGNING_KEY", raising=False)

    auth = MagicMock(spec=HTTPAuthorizationCredentials)
    auth.credentials = "some-token"

    with pytest.raises(HTTPException) as excinfo:
        _ = get_current_user(auth)

    assert excinfo.value.status_code == 500


@pytest.mark.usefixtures("mock_env_signing_key")
def test_get_current_user_expired_token(
    test_key_pair: tuple[ec.EllipticCurvePrivateKey, Mapping[str, object]],
) -> None:
    private_key, _ = test_key_pair
    import time

    payload = {"sub": "123", "exp": time.time() - 100, "aud": "authenticated"}
    token = jwt.encode(payload, private_key, algorithm="ES256")

    auth = MagicMock(spec=HTTPAuthorizationCredentials)
    auth.credentials = token

    with pytest.raises(HTTPException) as excinfo:
        _ = get_current_user(auth)

    assert excinfo.value.status_code == 401
    assert "Token has expired" in excinfo.value.detail


@pytest.mark.usefixtures("mock_env_signing_key")
def test_get_current_user_invalid_token() -> None:
    token = "invalid-token"

    auth = MagicMock(spec=HTTPAuthorizationCredentials)
    auth.credentials = token

    with pytest.raises(HTTPException) as excinfo:
        _ = get_current_user(auth)

    assert excinfo.value.status_code == 401
    assert "Invalid token" in excinfo.value.detail
