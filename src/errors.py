from typing import Any, Callable
from fastapi import FastAPI, status
from fastapi.requests import Request
from fastapi.responses import JSONResponse

class BooklyException(Exception):
    """This is the base class for all bookly exceptions"""
    pass

class InvalidToken(BooklyException):
    """User provided invalid or expired token"""
    pass

class RevokedToken(BooklyException):
    """User provided a token that has been revoked"""
    pass

class AccessTokenRequired(BooklyException):
    """User provided refresh token when access token is required"""
    pass

class InsufficientPermissionError(BooklyException):
    """User does not have requisit permission for this action"""
    pass

class AccountNotVerifiedError(BooklyException):
    """User account is not verified"""
    pass

class AccessDeniedError(BooklyException):
    """User does not have valid token"""
    pass 

class DataAlreadyExistError(BooklyException):
    """Data already exists"""
    pass

def create_exception_handler(status_code:int, initial_detail: Any) -> Callable[[Request, Exception], JSONResponse]:
    async def exception_handler(request: Request, exc: BooklyException):
        return JSONResponse(
            content=initial_detail,
            status_code=status_code
        )
    
    return exception_handler


def register_all_errors(app: FastAPI):
    #repeat for all other error handlers
    app.add_exception_handler(
        InvalidToken,
        create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            initial_detail={
                "message": "Token is invalid or expired",
                "error_code": "invalid_token",
            },
        ),
    )

    app.add_exception_handler(
        InsufficientPermissionError,
        create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            initial_detail={
                "message": "User does not have permission",
                "error_code": "insufficient_permission"
            },
        )
    )

    app.add_exception_handler(
        AccountNotVerifiedError,
        create_exception_handler(
            status_code=status.HTTP_403_FORBIDDEN,
            initial_detail={
                "message": "Account not verified",
                "error_code": "account_not_verified",
                "resolution": "Please check your email for verification details"
            },
        )
    )

    app.add_exception_handler(
     AccessDeniedError,
        create_exception_handler(
            status_code=status.HTTP_403_FORBIDDEN,
            initial_detail={
                "message": "Invalid or Expired Token",
                "error_code": "invalid_token",
                "resolution": "Please provide the correct email or password"
            }
        )
    )

    @app.exception_handler(500)
    async def internal_server_error(request, exec):
        return JSONResponse(
            content={
                "message": "Oops! Something went wrong",
                "error_code": "server_error"
            },
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
