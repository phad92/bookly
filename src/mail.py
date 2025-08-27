from typing import List
from fastapi_mail import FastMail, ConnectionConfig, MessageSchema, MessageType
from pathlib import Path
from src.config import Config

BASE_DIR = Path(__file__).resolve().parent

MAIL_CONFIG = ConnectionConfig(
    MAIL_USERNAME=Config.MAIL_JET_ACTIVATION_KEY,
    MAIL_PASSWORD=Config.MAIL_JET_SECRET_KEY,
    MAIL_FROM=Config.MAIL_FROM,
    MAIL_PORT=Config.MAIL_PORT,
    MAIL_SERVER=Config.MAIL_JET_SERVER_URL,
    MAIL_DEBUG=Config.MAIL_DEBUG,
    MAIL_STARTTLS=Config.MAIL_STARTTLS,
    MAIL_SSL_TLS=Config.MAIL_SSL_TLS,
    USE_CREDENTIALS=True,
    TEMPLATE_FOLDER=Path(BASE_DIR, 'templates')
)

mail = FastMail(
    config=MAIL_CONFIG
)


def create_message(recipients: List[str], subject: str, body: str):
    message = MessageSchema(recipients=recipients, subject=subject, body=body,subtype=MessageType.html)

    return message
