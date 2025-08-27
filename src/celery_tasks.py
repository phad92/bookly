from typing import List
from celery import Celery
from asgiref.sync import async_to_sync
from src.mail import mail, create_message

c_app = Celery('Tasks')

c_app.config_from_object('src.config')

@c_app.task
def send_email(recipients: List[str], subject: str, body: str):
    message = create_message(
        recipients=recipients, subject=subject, body=body
    )

    async_to_sync(mail.send_message)(message)
    # bg_tasks.add_task(mail.send_message, message)  # await mail.send_message(message)



# celery -A src.celery_tasks.c_app worker  --pool=solo --loglevel=info (command to run worker)