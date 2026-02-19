"""
Email service - handles sending emails via SMTP.
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from pathlib import Path
from typing import List, Optional

from app.config import settings
from app.logging_config import get_logger

logger = get_logger(__name__)


class EmailService:
    """Service for sending emails via SMTP."""
    
    def __init__(self):
        """Initialize email service with SMTP settings."""
        self.smtp_host = settings.smtp_host
        self.smtp_port = settings.smtp_port
        self.smtp_user = settings.smtp_user
        self.smtp_password = settings.smtp_password
        self.smtp_from = settings.smtp_from
        self.smtp_use_tls = settings.smtp_use_tls
    
    def send_email_with_attachments(
        self,
        to_email: str,
        subject: str,
        body: str,
        attachment_paths: Optional[List[str]] = None,
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None
    ) -> bool:
        """
        Send an email with optional attachments.
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            body: Email body (plain text)
            attachment_paths: List of file paths to attach
            cc: List of CC email addresses
            bcc: List of BCC email addresses
        
        Returns:
            True if email was sent successfully, False otherwise
        """
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.smtp_from
            msg['To'] = to_email
            msg['Subject'] = subject
            
            if cc:
                msg['Cc'] = ', '.join(cc)
            if bcc:
                msg['Bcc'] = ', '.join(bcc)
            
            # Add body
            msg.attach(MIMEText(body, 'plain'))
            
            # Add attachments
            if attachment_paths:
                for file_path in attachment_paths:
                    path = Path(file_path)
                    if path.exists():
                        with open(path, 'rb') as file:
                            part = MIMEApplication(file.read(), Name=path.name)
                            part['Content-Disposition'] = f'attachment; filename="{path.name}"'
                            msg.attach(part)
            
            # Connect to SMTP server and send
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                if self.smtp_use_tls:
                    server.starttls()
                
                server.login(self.smtp_user, self.smtp_password)
                
                # Prepare recipients
                recipients = [to_email]
                if cc:
                    recipients.extend(cc)
                if bcc:
                    recipients.extend(bcc)
                
                server.send_message(msg, self.smtp_from, recipients)
            
            return True
        
        except Exception as e:
            logger.error("email_send_failed", error=str(e), to=to_email, subject=subject)
            return False
    
    def send_html_email(
        self,
        to_email: str,
        subject: str,
        html_body: str,
        text_body: Optional[str] = None,
        attachment_paths: Optional[List[str]] = None
    ) -> bool:
        """
        Send an HTML email with optional plain text fallback.
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            html_body: Email body (HTML)
            text_body: Plain text fallback (optional)
            attachment_paths: List of file paths to attach
        
        Returns:
            True if email was sent successfully, False otherwise
        """
        try:
            msg = MIMEMultipart('alternative')
            msg['From'] = self.smtp_from
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Add plain text and HTML parts
            if text_body:
                msg.attach(MIMEText(text_body, 'plain'))
            msg.attach(MIMEText(html_body, 'html'))
            
            # Add attachments
            if attachment_paths:
                for file_path in attachment_paths:
                    path = Path(file_path)
                    if path.exists():
                        with open(path, 'rb') as file:
                            part = MIMEApplication(file.read(), Name=path.name)
                            part['Content-Disposition'] = f'attachment; filename="{path.name}"'
                            msg.attach(part)
            
            # Send email
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                if self.smtp_use_tls:
                    server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)
            
            return True
        
        except Exception as e:
            logger.error("html_email_send_failed", error=str(e), to=to_email, subject=subject)
            return False


# Global instance
email_service = EmailService()
