import smtplib
import os
from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv()

def send_pdf_email(to_email: str, subject: str, body: str, pdf_bytes: bytes, pdf_filename: str) -> tuple[bool, str]:
    """
    Belirtilen adrese PDF ekli e-posta gönderir.
    .env dosyasındaki SMTP_SERVER, SMTP_PORT, SMTP_USER, SMTP_PASS ayarlarını kullanır.
    """
    smtp_server = os.getenv("SMTP_SERVER")
    smtp_port   = os.getenv("SMTP_PORT", "587")
    smtp_user   = os.getenv("SMTP_USER")
    smtp_pass   = os.getenv("SMTP_PASS")

    if not all([smtp_server, smtp_user, smtp_pass]):
        return False, "SMTP ayarları (.env) eksik. Lütfen .env dosyasına SMTP_SERVER, SMTP_PORT, SMTP_USER, SMTP_PASS ekleyin."

    try:
        msg = EmailMessage()
        msg['Subject'] = subject
        msg['From']    = smtp_user
        msg['To']      = to_email
        msg.set_content(body)

        msg.add_attachment(
            pdf_bytes,
            maintype='application',
            subtype='pdf',
            filename=pdf_filename
        )

        with smtplib.SMTP(smtp_server, int(smtp_port)) as server:
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.send_message(msg)
            
        return True, "E-posta başarıyla gönderildi!"
    except Exception as e:
        return False, f"Gönderim hatası: {str(e)}"
