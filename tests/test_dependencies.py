import pytest
from pytest_mock import MockerFixture
from typing import cast
from collections.abc import Generator
from unittest.mock import MagicMock, patch
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from dependencies import get_current_user
from supabase import Client
from supabase_auth import User

# Mock user data
mock_user_data = MagicMock(spec=User)
mock_user_data.id = "test-uid"
mock_user_data.email = "test@example.com"


@pytest.fixture
def mock_supabase() -> Generator[Client, None, None]:
    with patch("dependencies.supabase") as mock:
        yield cast(Client, mock)


def test_get_current_user_success(mock_supabase: Client, mocker: MockerFixture) -> None:
    mock_get_user = mocker.patch.object(
        mock_supabase.auth, "get_user", return_value=MagicMock(user=mock_user_data)
    )

    auth = MagicMock(spec=HTTPAuthorizationCredentials)
    auth.credentials = "valid-token"

    user = get_current_user(auth)

    assert user == mock_user_data
    mock_get_user.assert_called_once_with("valid-token")


def test_get_current_user_invalid_token(
    mock_supabase: Client, mocker: MockerFixture
) -> None:
    _ = mocker.patch.object(
        mock_supabase.auth.get_user, "return_value", MagicMock(user=None)
    )

    auth = MagicMock(spec=HTTPAuthorizationCredentials)
    auth.credentials = "invalid-token"

    with pytest.raises(HTTPException) as excinfo:
        _ = get_current_user(auth)

    assert excinfo.value.status_code == 401
    assert "Invalid authentication credentials" in excinfo.value.detail


def test_get_current_user_supabase_error(
    mock_supabase: Client, mocker: MockerFixture
) -> None:
    _ = mocker.patch.object(
        mock_supabase.auth.get_user, "side_effect", Exception("Supabase Error")
    )

    auth = MagicMock(spec=HTTPAuthorizationCredentials)
    auth.credentials = "any-token"

    with pytest.raises(HTTPException) as excinfo:
        _ = get_current_user(auth)

    assert excinfo.value.status_code == 401
    assert "Could not validate credentials" in excinfo.value.detail
