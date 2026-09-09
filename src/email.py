import os
import smtplib
from src.logger import logger
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from src.config import config




def send_email(to_email: str, subject: str, body: str) -> bool:
    """
    Send an email using Gmail SMTP.

    Args:
        to_email: Recipient email address
        subject: Email subject
        body: Email body

    Returns:
        True if email was sent successfully, False otherwise.
    """

    # Read credentials from environment variables
    sender_email = config.sender_email
    app_password = config.app_password
    smtp_host = config.EMAIL['smtp_host']
    smtp_port = config.EMAIL['smtp_port']
    enabled = config.EMAIL['enabled']

    if not enabled:
        logger.warning("Sending E-mails not enabled.")
        return False

    # Validate credentials
    if not sender_email:
        logger.error("EMAIL_ADDRESS environment variable is missing.")
        return False

    if not app_password:
        logger.error("EMAIL_APP_PASSWORD environment variable is missing.")
        return False

    if not to_email:
        logger.error("Recipient email address is missing.")
        return False

    if not subject:
        logger.error("Email subject is missing.")
        return False

    if not body:
        logger.error("Email body is missing.")
        return False

    try:
        # Create email
        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = to_email
        message["Subject"] = subject

        # Add email body
        message.attach(MIMEText(body, "plain"))

        # Connect to Gmail SMTP server
        with smtplib.SMTP(smtp_host, smtp_port, timeout=30) as server:

            # Enable TLS encryption
            server.starttls()

            # Login using Gmail App Password
            server.login(sender_email, app_password)

            # Send email
            server.sendmail(
                sender_email,
                to_email,
                message.as_string()
            )

        logger.info(f"Email sent successfully to {to_email}")
        return True

    except smtplib.SMTPAuthenticationError:
        logger.error(
            "Authentication failed. Check your email address "
            "and Gmail App Password."
        )
        return False

    except smtplib.SMTPRecipientsRefused:
        logger.error(f"Recipient email was refused: {to_email}")
        return False

    except smtplib.SMTPException as e:
        logger.error(f"SMTP error occurred: {e}")
        return False

    except TimeoutError:
        logger.error("Connection to email server timed out.")
        return False

    except Exception as e:
        logger.exception(f"Unexpected error while sending email: {e}")
        return False