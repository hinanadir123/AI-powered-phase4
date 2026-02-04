from fastapi import HTTPException, status
from fastapi.responses import JSONResponse
from typing import Union
from ..models.user import User


class APIError:
    """Standardized API error responses."""
    
    @staticmethod
    def unauthorized(detail: str = "Unauthorized"):
        """Return unauthorized error response."""
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={
                "error": "Unauthorized",
                "detail": detail,
                "code": "AUTH_001"
            }
        )
    
    @staticmethod
    def forbidden(detail: str = "Forbidden"):
        """Return forbidden error response."""
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={
                "error": "Forbidden",
                "detail": detail,
                "code": "AUTH_002"
            }
        )
    
    @staticmethod
    def not_found(resource: str = "Resource", resource_id: str = None):
        """Return not found error response."""
        detail = f"{resource} not found"
        if resource_id:
            detail = f"{resource} with ID {resource_id} not found"
        
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "error": "Not Found",
                "detail": detail,
                "code": "RESOURCE_001"
            }
        )
    
    @staticmethod
    def bad_request(detail: str = "Bad Request"):
        """Return bad request error response."""
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "error": "Bad Request",
                "detail": detail,
                "code": "VALIDATION_001"
            }
        )
    
    @staticmethod
    def internal_error(detail: str = "Internal Server Error"):
        """Return internal server error response."""
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "Internal Server Error",
                "detail": detail,
                "code": "SERVER_001"
            }
        )


def handle_exception(exc: Exception) -> JSONResponse:
    """Generic exception handler."""
    if isinstance(exc, HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": "HTTP Exception",
                "detail": str(exc.detail),
                "code": f"HTTP_{exc.status_code}"
            }
        )
    
    # Log the error for debugging
    from ..core.logging import log_error
    log_error(f"Unhandled exception: {str(exc)}")
    
    return APIError.internal_error()


def validate_user_owns_resource(user: User, resource_user_id: str) -> bool:
    """Validate that the user owns the resource they're trying to access."""
    return user.id == resource_user_id