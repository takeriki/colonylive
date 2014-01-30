#!/usr/bin/python

import smtplib
from email import Encoders
from email.mime.text import MIMEText
from email.MIMEBase import MIMEBase
from email.MIMEMultipart import MIMEMultipart
from email.Header import Header

from clive.core.parameter import cfg
EMAIL = cfg.get('GENERAL','email_admin')

def send_mail(from_addr, to_addr, subject, body, attach=''):
    # Create a text/plain message
    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = from_addr
    msg['To'] = to_addr

    body = MIMEText(body)
    msg.attach(body)

    attachment = MIMEBase("application","vnd.ms-excel")
    if attach != "":
        f = open(attach)
        attachment.set_payload(f.read())
        f.close()
        Encoders.encode_base64(attachment)
        msg.attach(attachment)
        attachment.add_header("Content-Disposition","attachment", filename=attach)

    # Send the message via local SMTP server
    s = smtplib.SMTP('localhost')
    me = ''
    s.sendmail(me, [to_addr], msg.as_string())
    

if __name__ == '__main__':
    send_mail('Colony-live <clive@localhost>', EMAIL, 'test', 'body')
