"""
Two dependencies power every protected route:
  - get_current_user: decodes the JWT, loads the user, 401s on anything wrong
  - require_role(*roles): wraps get_current_user, 403s if the user's role
    isn't in the allowed set

A route declares its access rule in its signature -
`user: User = Depends(require_role("official"))` - so RBAC is visible at
the endpoint definition, not buried in an if-statement inside the body.
"""
import uuid

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.db.base import get_db
from app.db.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception

    user_id = payload.get("sub")
    if user_id is None:
        raise credentials_exception

    try:
        user = db.get(User, uuid.UUID(user_id))
    except (ValueError, TypeError):
        raise credentials_exception

    if user is None:
        raise credentials_exception
    return user


def require_role(*allowed_roles: str):
    def _guard(user: User = Depends(get_current_user)) -> User:
        if user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{user.role}' is not permitted to perform this action",
            )
        return user

    return _guard
