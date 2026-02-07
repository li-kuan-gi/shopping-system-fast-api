import inspect
from typing import Annotated, TypeVar, ParamSpec, Protocol
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from supabase_auth import User
from database import supabase

# Define parameter and return type variables for better type safety
P = ParamSpec("P")
R = TypeVar("R")


# Protocol to allow assigning to the __signature__ attribute
class HasSignature(Protocol):
    __signature__: inspect.Signature


# This scheme expects "Authorization: Bearer <token>"
# Using HTTPBearer instead of OAuth2PasswordBearer for better Swagger UI experience
security = HTTPBearer()


def get_current_user(
    auth: Annotated[HTTPAuthorizationCredentials, Depends(security)],
) -> User:
    """
    Verifies the JWT token using Supabase Auth.
    Returns the user data if valid.
    """
    try:
        # Verify the token via Supabase
        token = auth.credentials
        user = supabase.auth.get_user(token)
        if not user or not user.user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user.user
    except Exception as e:
        # If Supabase raises an error (e.g. invalid token)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Could not validate credentials: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )
