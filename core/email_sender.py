import smtplib
import ssl
import os
from email.message import EmailMessage


def send_pdf_email(
    to_email: str,
    subject: str,
    body: str,
    pdf_bytes: bytes,
    pdf_filename: str,
) -> tuple[bool, str]:
    """
    Belirtilen adrese PDF ekli e-posta gönderir.
    Ortam değişkenleri app.py'deki load_dotenv() ile zaten yüklenmiş olur.
    Gmail için Uygulama Şifresi (App Password) kullanılmalıdır.
    """
    smtp_server = os.environ.get("SMTP_SERVER", "smtp.gmail.com")
    smtp_port   = int(os.environ.get("SMTP_PORT", "587"))
    smtp_user   = os.environ.get("SMTP_USER", "")
    smtp_pass   = os.environ.get("SMTP_PASS", "")

    if not smtp_user or not smtp_pass:
        return False, (
            "❌ .env dosyasında SMTP_USER veya SMTP_PASS tanımlı değil. "
            "Proje klasöründe .env dosyasının olduğundan emin olun."
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

    # Yöntem 1: Port 587 STARTTLS
    try:
        with smtplib.SMTP(smtp_server, 587, timeout=15) as server:
            server.ehlo()
            server.starttls(context=ssl.create_default_context())
            server.ehlo()
            server.login(smtp_user, smtp_pass)
            server.send_message(msg)
        return True, f"✅ E-posta başarıyla gönderildi → {to_email}"

    except smtplib.SMTPAuthenticationError:
        return False, (
            "❌ Gmail kimlik doğrulama hatası.\n\n"
            "Normal hesap şifresi SMTP için çalışmaz. Çözüm:\n"
            "1. Gmail → Ayarlar → Güvenlik → 2 Adımlı Doğrulama'yı açın\n"
            "2. https://myaccount.google.com/apppasswords adresine gidin\n"
            "3. 'Diğer' seçin → 'FIGES CV' yazın → Oluştur\n"
            "4. Çıkan 16 haneli şifreyi .env dosyasındaki SMTP_PASS'e yazın"
        )

    except Exception as e1:
        # Yöntem 2: Port 465 SSL
        try:
            with smtplib.SMTP_SSL(smtp_server, 465,
                                  context=ssl.create_default_context(),
                                  timeout=15) as server:
                server.login(smtp_user, smtp_pass)
                server.send_message(msg)
            return True, f"✅ E-posta başarıyla gönderildi → {to_email}"
        except Exception as e2:
            return False, f"❌ Gönderim hatası: {str(e2)}"
