

# -*- coding: utf-8 -*-
from models.MongoDB import MongoDB
file = open("C:\\Users\\hkarri\\Documents\\hck\\GH2019\\static\\images\\car1.jpg")
m=MongoDB()
m.saveCarToDB("SpeedCam1","H786P0J","Waiting","car2.jpg","cam1")
#m.addCarToFloor("H786P0J","car3.jpg","cam1","2",-1)
"""
from flask import Flask
from flask_mail import Mail
from flask_mail import Message

app = Flask(__name__)
mail = Mail(app)


#app.config['MAIL_SERVER']='smtp.gmail.com'
#app.config['MAIL_PORT'] = 465
app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 56444
app.config['MAIL_USERNAME'] = 'no.overspeeding@gmail.com'
app.config['MAIL_PASSWORD'] = 'goslow@123'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True

msg = Message('Hello', sender = 'no.overspeeding@gmail.com', recipients = ['cse.14908@gmail.com'])
msg.body = "This is the email body"
mail.send(msg)


from email.mime.text import MIMEText
from subprocess import Popen, PIPE

msg = MIMEText("Hello guys")
msg["From"] = "cse.14908@gmail.com"
msg["To"] = 'no.overspeeding@gmail.com'
msg["Subject"] = "Python sendmail test"
p = Popen(["/usr/sbin/sendmail", "-t", "-oi"], stdin=PIPE)
p.communicate(msg.as_bytes())


"""

"""
# Python code to illustrate Sending mail from
# your Gmail account
import smtplib

# creates SMTP session
s = smtplib.SMTP('smtp.gmail.com', 587)

# start TLS for security
s.starttls()

# Authentication
s.login("no.overspeeding@gmail.com", "goslow@123")

# message to be sent
message = "Message_you_need_to_send"

# sending the mail
s.sendmail("no.overspeeding@gmail.com", "cse.14908@gmail.com", message)

# terminating the session
s.quit()

"""


# Python code to illustrate Sending mail with attachments
# from your Gmail account

# libraries to be imported
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

fromaddr = "no.overspeeding@gmail.com"
toaddr = "cse.14908@gmail.com"

# instance of MIMEMultipart
msg = MIMEMultipart()

# storing the senders email address
msg['From'] = fromaddr

# storing the receivers email address
msg['To'] = toaddr

# storing the subject
msg['Subject'] = "Subject of the Mail"

# string to store the body of the mail
body = "Body of email"

# attach the body with the msg instance
msg.attach(MIMEText(body, 'plain'))

# open the file to be sent
filename = "car1.jpg"
attachment = open("D:\SpyderDev\FlaskAppGH19\static\images\car1.jpg", "rb")

# instance of MIMEBase and named as p
p = MIMEBase('application', 'octet-stream')

# To change the payload into encoded form
p.set_payload((attachment).read())

# encode into base64
encoders.encode_base64(p)

p.add_header('Content-Disposition', "attachment; filename= %s" % filename)

# attach the instance 'p' to instance 'msg'
msg.attach(p)

# creates SMTP session
s = smtplib.SMTP('smtp.gmail.com', 587)

# start TLS for security
s.starttls()

# Authentication
s.login(fromaddr, "goslow@123")

# Converts the Multipart msg into a string
text = msg.as_string()

# sending the mail
s.sendmail(fromaddr, toaddr, text)

# terminating the session
s.quit()

#import csv
def dummy():
    fname="car1.jpg"
    fields = [fname]
    with open('fname.csv', mode='w') as img_fileName:
        csv_writer = csv.writer(img_fileName, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        csv_writer.writerow(fields)

import csv
def read2():
    f = open("fname.csv", 'rt')

    try:
        reader = csv.reader(f)
        row1 = next(reader)
        print(row1[0])

    finally:
        f.close()
