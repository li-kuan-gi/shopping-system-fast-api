import inspect
from functools import wraps
from typing import Annotated, Callable, TypeVar, ParamSpec, cast, Protocol
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


def login_required(func: Callable[P, R]) -> Callable[P, R]:
    """
    Decorator that injects get_current_user dependency into the function signature.
    This allows the route to be protected and shows up correctly in Swagger UI.
    """
    sig = inspect.signature(func)
    params = list(sig.parameters.values())

    # Create a wrapper that removes the injected '_user' before calling the actual function
    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        # We cast kwargs to dict to safely pop the injected parameter
        _ = cast(dict[str, object], kwargs).pop("_user", None)
        return func(*args, **kwargs)

    # Add _user parameter with Depends(get_current_user) if not already present
    if "_user" not in sig.parameters:
        new_param = inspect.Parameter(
            "_user",
            inspect.Parameter.KEYWORD_ONLY,
            default=Depends(get_current_user),
        )
        params.append(new_param)
        # Update the wrapper's signature so FastAPI can see the new parameter
        # Use HasSignature protocol to satisfy pyright. Cast through object to avoid overlap errors.
        cast(HasSignature, cast(object, wrapper)).__signature__ = sig.replace(
            parameters=params
        )

    return wrapper
