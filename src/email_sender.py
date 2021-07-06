# encoding: utf-8

"""Script para enviar email"""

import json
import smtplib
import ssl
import email.utils
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os.path

# Replace sender@example.com with your "From" address.
# This address must be verified.
SENDER = 'noreply@alejodeveloper.com'
SENDERNAME = 'Alejodeveloper'

# Replace recipient@example.com with a "To" address. If your account
# is still in the sandbox, this address must be verified.

# Secrets
THIS_FILE_DIR = '/'.join(os.path.realpath(__file__).split('/')[0:-1])
secrets = json.load(open(f'{THIS_FILE_DIR}/secrets.json'))

# Replace smtp_username with your Amazon SES SMTP user name.
USERNAME_SMTP = secrets['smtp_user']

# Replace smtp_password with your Amazon SES SMTP password.
PASSWORD_SMTP = secrets['smtp_password']

# If you're using Amazon SES in an AWS Region other than US West (Oregon),
# replace email-smtp.us-west-2.amazonaws.com with the Amazon SES SMTP
# endpoint in the appropriate region.
HOST = "smtp.hostinger.com"
PORT = 465

def send_email(contenido: dict):
    """Crea y envía los mensajes

    El parámetro contenido es un diccionario con las siguientes llaves:
    subject: Asunto del correo
    recipient: Destinatirio del correo, un único correo electrónico
    plain: Opcional, contenido del mensaje en formato plano
    html: Opcional, contenido del mensaje en html
    """
    # Create message container - the correct MIME type is multipart/alternative.
    msg = MIMEMultipart('alternative')
    msg['Subject'] = contenido['subject']
    msg['From'] = email.utils.formataddr((SENDERNAME, SENDER))
    msg['To'] = contenido['recipient']

    # Record the MIME types of both parts - text/plain and text/html.
    if 'plain' in contenido:
        msg.attach(MIMEText(contenido['plain'], 'plain'))
    if 'html' in contenido:
        msg.attach(MIMEText(contenido['html'], 'html'))

    # Try to send the message.
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(HOST, PORT, context=context) as server:
        server.login(USERNAME_SMTP, PASSWORD_SMTP)
        server.sendmail(SENDER, contenido['recipient'], msg.as_string())
        print("Email sent!")

