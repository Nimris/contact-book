from fastapi_mail import ConnectionConfig, FastMail, MessageSchema
from config.general import settings
import logging

mail_config = ConnectionConfig(
    MAIL_USERNAME=settings.mail_username, 
    MAIL_PASSWORD=settings.mail_password, 
    MAIL_FROM=settings.mail_from,
    MAIL_PORT=settings.mail_port,
    MAIL_SERVER=settings.mail_server,       # "host.docker.internal"
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    MAIL_DEBUG=True,
    )


logger = logging.getLogger("email_logger")

async def send_verification_email(email: str, email_body: str):
    logger.info(f"Отправка письма на {email}")
    message = MessageSchema(
        subject="Email Verification",
        recipients=[email],
        body=email_body,
        subtype="html"
    )
    fm = FastMail(mail_config)
    try:
        await fm.send_message(message)
        logger.info(f"Письмо успешно отправлено на {email}")
    except Exception as e:
        logger.error(f"Ошибка отправки письма: {e}")