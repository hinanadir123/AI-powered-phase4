from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import jwt
import os
from dotenv import load_dotenv
from typing import Optional

load_dotenv()

security = HTTPBearer()
SECRET_KEY = os.getenv("BETTER_AUTH_SECRET") or os.getenv("BETTER_AUTH_JWT_SECRET")

if not SECRET_KEY:
    # For development purposes, we'll use a default secret
    # In production, this should be a strong, randomly generated secret
    SECRET_KEY = "dev-secret-key-change-in-production"
    print("WARNING: Using default development secret. Set BETTER_AUTH_SECRET environment variable for production.")

AUTH_URL = os.getenv("BETTER_AUTH_URL")

class TokenData(BaseModel):
    user_id: str


def verify_token(token: str) -> Optional[TokenData]:
    """
    Verify the JWT token and return the user_id if valid
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        user_id: str = payload.get("userId")

        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return TokenData(user_id=user_id)
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Dependency to get the current user from the JWT token
    """
    token = credentials.credentials
    token_data = verify_token(token)
    return token_data.user_id


# Export SECRET_KEY for use in other modules
__all__ = ["SECRET_KEY", "get_current_user", "TokenData", "verify_token"]