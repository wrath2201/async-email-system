import os 
import smtplib
from email.message import EmailMessage

def send_email(to_email:str , subject:str , body:str):
    msg=EmailMessage()
    msg["From"]=os.getenv("EMAIL_FROM")
    msg["To"]=to_email
    msg["Subject"]=subject
    msg.set_content(body)

    server=smtplib.SMTP(os.getenv("SMTP_HOST"),int(os.getenv("SMTP_PORT")))
    try:
        server.ehlo()  #handshake
        server.starttls()
        server.ehlo() # re-identify after tls
        server.login(
            os.getenv("SMTP_USERNAME"),
            os.getenv("SMTP_PASSWORD"),
        )
        server.send_message(msg)
    finally:
        server.quit()
