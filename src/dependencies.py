from dataclasses import dataclass
import os
import jwt
import json
from typing import Annotated, cast
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jwt import PyJWK

# This scheme expects "Authorization: Bearer <token>"
# We set auto_error=False so we can manually handle missing credentials
# and return 401 Unauthorized instead of the default 403 Forbidden.
security = HTTPBearer(auto_error=False)


@dataclass
class User:
    id: str


def get_current_user(
    auth: Annotated[HTTPAuthorizationCredentials | None, Depends(security)],
) -> User:
    """
    Verifies the JWT token locally using the Supabase JWT secret.
    Returns the decoded token payload if valid.
    """
    if auth is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = auth.credentials
    secret = os.environ.get("SUPABASE_JWT_SIGNING_KEY")

    if not secret:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    jwk_data = cast(dict[str, object], json.loads(secret))
    jwk = PyJWK(jwk_data)

    try:
        # Verify the token using PyJWT
        payload = jwt.decode(
            token,
            jwk,
            algorithms=["ES256"],
            audience="authenticated",
            options={"verify_aud": True},
        )
        user_id = payload.get("sub")
        if not user_id or not isinstance(user_id, str):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User ID not found in token",
            )
        return User(id=user_id)
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


from sqlalchemy.orm import Session
from src.database import get_db
from src.services.cart import CartService


def get_cart_service(db: Annotated[Session, Depends(get_db)]) -> CartService:
    return CartService(db)
