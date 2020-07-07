import json
from email.mime.text import MIMEText
import smtplib

import os

gmailUser = os.environ.get('SenderAccount', '')
gmailPasswd = os.environ.get('SenderPwd', '')

def sendEmail():
    to = ['song046@gmail.com']

    # Create message
    emails = [t.split(',') for t in to]
    message = MIMEText('Give me a Test!', 'plain', 'utf-8')
    message['Subject'] = 'Single Test'
    message['From'] = gmailUser
    message['To'] = ','.join(to)

    # Set smtp
    smtp = smtplib.SMTP("smtp.gmail.com:587")
    smtp.ehlo()
    smtp.starttls()
    smtp.login(gmailUser, gmailPasswd)

    # Send msil
    smtp.sendmail(message['From'], message['To'], message.as_string())
    return 'Send mails OK!'