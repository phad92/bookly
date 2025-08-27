from datetime import datetime, timedelta
import email
import logging
from tkinter import N
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.responses import JSONResponse
from src.celery_tasks import send_email
from src import mail
from src.auth.dependencies import (
    AccessTokenBearer,
    RefreshTokenBearer,
    RoleChecker,
    get_current_user,
)
from src.db.main import get_session
from src.config import Config
from sqlmodel.ext.asyncio.session import AsyncSession

from src.db.redis import add_jti_to_blocklist
from src.errors import AccessDeniedError
from src.mail import create_message, mail
from .schemas import (
    EmailModel,
    PasswordResetConfirmModel,
    PasswordResetRequestModel,
    UserBooksModel,
    UserCreateModel,
    UserLoginModel,
    UserModel,
)
from .service import UserService
from .utils import (
    create_access_token,
    create_url_safe_token,
    decode_token,
    decode_url_safe_token,
    generate_passwd_hash,
    verify_password,
)

auth_router = APIRouter()
user_service = UserService()
role_checker = RoleChecker(["admin", "user"])

REFRESH_TOKEN_EXPIRY = 2


@auth_router.post("/signup", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_user_account(
    user_data: UserCreateModel, bg_tasks: BackgroundTasks, session: AsyncSession = Depends(get_session)
):
    email = user_data.email

    user_exists = await user_service.user_exists(email, session)

    if user_exists:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User with email already exists",
        )

    new_user = await user_service.create_user(user_data, session)

    token = create_url_safe_token({"email": email})
    link = f"http://{Config.DOMAIN}/api/v1/auth/verify/{token}"

    html_message = f"""
    <h1>Verify your email</h1>
    <p>Please click this <a href="{link}">link</a> to verify your email</p>
    """

    subject = "Verify your email"

    send_email.delay([email], subject, html_message)

    


    # message = create_message(
    #     recipients=[email], subject="Verify your email", body=html_message
    # )
    # bg_tasks.add_task(mail.send_message, message) #await mail.send_message(message)
    return {
        "message": "Account created! check email to verify your account",
        "user": new_user,
    }


@auth_router.get("/verify/{token}")
async def verify_user_account(token: str, session: AsyncSession = Depends(get_session)):
    token_data = decode_url_safe_token(token)
    user_email = token_data.get("email")

    if user_email:
        user = await user_service.get_user_by_email(user_email, session)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="user not found"
            )  # UserNotFound Exception
        await user_service.update_user(user, {"is_verified": True}, session)

        return JSONResponse(
            content={"message": "Account verified successfully"},
            status_code=status.HTTP_200_OK,
        )

    return JSONResponse(
        content={"message": "Error occured during verification"},
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


@auth_router.post("/login")
async def login_user(
    login_data: UserLoginModel, session: AsyncSession = Depends(get_session)
):
    email = login_data.email
    password = login_data.password

    user = await user_service.get_user_by_email(email, session)

    if user is not None:
        password_valid = verify_password(password, user.password_hash)

        if password_valid:
            access_token = create_access_token(
                user_data={
                    "email": email,
                    "user_uid": str(user.uid),
                    "role": user.role,
                },
            )

            refresh_token = create_access_token(
                user_data={
                    "email": email,
                    "user_uid": str(user.uid),
                    "role": user.role,
                },
                expiry=timedelta(days=REFRESH_TOKEN_EXPIRY),
                refresh=True,
            )

            return JSONResponse(
                content={
                    "message": "login successful",
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "user": {"email": user.email, "uid": str(user.uid)},
                }
            )

        raise AccessDeniedError()


@auth_router.get("/refresh_token")
async def get_new_access_token(token_details: dict = Depends(RefreshTokenBearer())):
    exp_timpstamp = token_details["exp"]

    if datetime.fromtimestamp(exp_timpstamp) > datetime.now():
        new_access_token = create_access_token(user_data=token_details["user"])

        return JSONResponse(content={"access_token": new_access_token})

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired token"
    )


@auth_router.get("/me", response_model=UserBooksModel)
async def get_current_user(
    user=Depends(get_current_user), _: bool = Depends(role_checker)
):
    return user


@auth_router.get("/logout")
async def revoke_token(token_details: dict = Depends(AccessTokenBearer())):
    jti = token_details["jti"]

    await add_jti_to_blocklist(jti)

    return JSONResponse(
        content={"message": "Logged out successfully"}, status_code=status.HTTP_200_OK
    )


@auth_router.post("/send_mail")
async def send_email_test(emails: EmailModel):
    try:

        emails = emails.addresses
        
        html = "<h1>Welcome to bookly app</h1>"
        message = create_message(emails, subject="Hello!, Welcome", body=html)
        
        await mail.send_message(message)
        return {"message": "Email successfully sent!!!"}
    except Exception as e:
        logging.exception(e)
        return {"message": "failed to send mail"}


"""
1. Provide email -> password reset request
2. Send password reset link
3. Reset password -> password reset confirmation
"""

@auth_router.post('/password-reset')
async def password_reset(email_data: PasswordResetRequestModel):
    email = email_data.email

    token = create_url_safe_token({"email": email})
    link = f"http://{Config.DOMAIN}/api/v1/auth/password-reset-confirm/{token}"

    html_message = f"""
    <h1>Reset your password</h1>
    <p>Please click this <a href="{link}">link</a> to reset your password</p>
    """

    message = create_message(
        recipients=[email], subject="Reset your password", body=html_message
    )
    await mail.send_message(message)

    emails = [email]
    subject = "Reset your password"
    send_email.delay(emails, subject, html_message)
    # return new_user
    return JSONResponse(content= {
        "message": "Please check your email for instruction to reset your password"
    }, status_code=status.HTTP_200_OK)

@auth_router.post('/password-reset-confirm/{token}')
async def reset_account_password(token: str, passwords: PasswordResetConfirmModel, session: AsyncSession= Depends(get_session)):
    token_data = decode_url_safe_token(token)
    user_email = token_data.get("email")

    if passwords.new_password != passwords.confirm_password:
        raise HTTPException(detail="Passwords do not match", status_code = status.HTTP_400_BAD_REQUEST)

    password_hash = generate_passwd_hash(passwords.new_password)
    if user_email:
        user = await user_service.get_user_by_email(user_email, session)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="user not found"
            )  # UserNotFound Exception
        await user_service.update_user(user, {"password_hash": password_hash}, session)

        return JSONResponse(
            content={"message": "Password reset successfully"},
            status_code=status.HTTP_200_OK,
        )

    return JSONResponse(
        content={"message": "Error occured during password reset"},
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
