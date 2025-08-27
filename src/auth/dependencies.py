from typing import List
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlmodel.ext.asyncio.session import AsyncSession
from src.db.models import User
from src.auth.service import UserService
from src.db.main import get_session
from src.db.redis import token_in_blocklist
from src.errors import (
    AccountNotVerifiedError,
    InsufficientPermissionError,
    InvalidToken,
)

from .utils import decode_token

user_service = UserService()


class TokenBearer(HTTPBearer):
    def __init__(self, auto_error=True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> HTTPAuthorizationCredentials | None:
        creds = await super().__call__(request)
        token = creds.credentials

        if not self.token_valid(token):
            raise InvalidToken()

        token_data = decode_token(token)
        # if token_data['refresh']:
        #     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="please provide and access token")

        if await token_in_blocklist(token_data["jti"]):
            raise InvalidToken()
            # raise InvalidToken(status_code=status.HTTP_403_FORBIDDEN, detail={
            #     "error": "expired or revoked token",
            #     "resolution": "Please get new token"
            # })

        self.verify_token_data(token_data)
        return token_data

    def verify_token_data(self, token_data):
        raise NotImplementedError("Please Override this method in chiled classes")

    def token_valid(self, token: str) -> bool:
        token_data = decode_token(token)
        return True if token_data is not None else False


class AccessTokenBearer(TokenBearer):
    def verify_token_data(self, token_data: dict) -> None:
        if token_data and token_data["refresh"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="please provide an access token",
            )


class RefreshTokenBearer(TokenBearer):
    def verify_token_data(self, token_data: dict) -> None:
        if token_data and not token_data["refresh"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="please provide a refresh token",
            )


async def get_current_user(
    token_details: dict = Depends(AccessTokenBearer()),
    session: AsyncSession = Depends(get_session),
):
    user_email = token_details["user"]["email"]

    user = await user_service.get_user_by_email(user_email, session)

    return user


class RoleChecker:
    def __init__(self, allowed_roles: List[str]) -> None:
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: User = Depends(get_current_user)):

        if not current_user.is_verified:
            raise AccountNotVerifiedError()

        if current_user.role in self.allowed_roles:
            return True

        raise InsufficientPermissionError()
        # raise HTTPException(
        #     status_code=status.HTTP_403_FORBIDDEN,
        #     detail="access denied"
        # )
