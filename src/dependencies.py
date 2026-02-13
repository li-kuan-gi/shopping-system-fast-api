import os
import jwt
import json
from typing import Annotated, cast
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jwt import PyJWK

# This scheme expects "Authorization: Bearer <token>"


def get_current_user(
    auth: Annotated[HTTPAuthorizationCredentials, Depends(security)],
) -> dict[str, object]:
    """
    Verifies the JWT token locally using the Supabase JWT secret.
    Returns the decoded token payload if valid.
    """
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
        return payload
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
