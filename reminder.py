# reminder.py
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from dotenv import load_dotenv

# Load variabel dari .env
load_dotenv()

SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
SENDER_EMAIL = os.getenv("SENDGRID_SENDER_EMAIL")
SENDER_NAME = os.getenv("MAIL_FROM_NAME", "Chatbot_Reminder")

def send_email(to_email: str, subject: str, html_content: str):
    """
    Mengirim email menggunakan Twilio SendGrid
    """
    if not SENDGRID_API_KEY or not SENDER_EMAIL:
        raise ValueError("API Key atau sender email belum diatur di .env")

    message = Mail(
        from_email=(SENDER_EMAIL, SENDER_NAME),
        to_emails=to_email,
        subject=subject,
        html_content=html_content
    )

    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)

        print("Status Code:", response.status_code)
        print("Response Body:", response.body)
        print("Response Headers:", response.headers)

        if response.status_code == 202:
            print(f"✅ Email berhasil dikirim ke {to_email}")
        else:
            print(f"⚠️ Email gagal dikirim, status_code={response.status_code}")

    except Exception as e:
        print("❌ Gagal mengirim email:", e)
        raise e


if __name__ == "__main__":
    # Contoh kirim email
    send_email(
        to_email="target_email@example.com",
        subject="Tes Kirim Email",
        html_content="<h1>Hello</h1><p>Ini email tes dari Chatbot Reminder 🚀</p>"
    )
