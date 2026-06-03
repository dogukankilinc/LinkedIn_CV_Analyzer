import smtplib
import ssl
import os
from pathlib import Path
from email.message import EmailMessage
from dotenv import load_dotenv

# .env her zaman proje kökünden yüklenir (core/ altından çağrılsa bile)
_ENV_PATH = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=_ENV_PATH, override=True)


def send_pdf_email(
    to_email: str,
    subject: str,
    body: str,
    pdf_bytes: bytes,
    pdf_filename: str,
) -> tuple[bool, str]:
    """
    Belirtilen adrese PDF ekli e-posta gönderir.
    Gmail için 'Uygulama Şifresi' (App Password) kullanılmalıdır.
    Önce Port 587 (STARTTLS), başarısız olursa Port 465 (SSL) ile dener.
    """
    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port   = int(os.getenv("SMTP_PORT", "587"))
    smtp_user   = os.getenv("SMTP_USER", "")
    smtp_pass   = os.getenv("SMTP_PASS", "")

    if not smtp_user or not smtp_pass:
        return False, (
            "❌ SMTP ayarları eksik. "
            ".env dosyasında SMTP_USER ve SMTP_PASS tanımlı olmalıdır."
        )

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"]    = f"FIGES CV Analyzer <{smtp_user}>"
    msg["To"]      = to_email
    msg.set_content(body)
    msg.add_attachment(
        pdf_bytes,
        maintype="application",
        subtype="pdf",
        filename=pdf_filename,
    )

    # ─── Yöntem 1: Port 587 STARTTLS ──────────────────────────────
    try:
        with smtplib.SMTP(smtp_server, 587, timeout=15) as server:
            server.ehlo()
            server.starttls(context=ssl.create_default_context())
            server.ehlo()
            server.login(smtp_user, smtp_pass)
            server.send_message(msg)
        return True, f"✅ E-posta başarıyla gönderildi → {to_email}"
    except smtplib.SMTPAuthenticationError:
        # Gmail'de normal şifre kabul edilmez; App Password gerekir
        return False, (
            "❌ Gmail kimlik doğrulama hatası.\n\n"
            "Gmail, normal hesap şifresini SMTP için **kabul etmiyor**.\n"
            "Çözüm:\n"
            "1. Gmail hesabında **2 Adımlı Doğrulama** açık olmalı.\n"
            "2. https://myaccount.google.com/apppasswords adresine gidin.\n"
            "3. 'Uygulama Seç → Diğer (özel ad)' → 'FIGES CV Analyzer' yazın → Oluştur.\n"
            "4. Oluşan **16 haneli şifreyi** .env dosyasındaki `SMTP_PASS` satırına yapıştırın.\n"
            "5. Uygulamayı yeniden başlatın."
        )
    except Exception as e:
        # ─── Yöntem 2: Port 465 SSL ───────────────────────────────
        try:
            with smtplib.SMTP_SSL(smtp_server, 465,
                                  context=ssl.create_default_context(),
                                  timeout=15) as server:
                server.login(smtp_user, smtp_pass)
                server.send_message(msg)
            return True, f"✅ E-posta başarıyla gönderildi → {to_email}"
        except Exception as e2:
            return False, f"❌ Gönderim hatası (587 & 465 denendi):\n{str(e2)}"
