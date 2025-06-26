import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Sender credentials
sender_email = "aryanajayshah@gmail.com"
app_password = "vrxupzfxwzfhqego"  

# Recipient list
recipients = ["realajaryan@gmail.com", "aakriti.201201@ncit.edu.np"]

# Email content
subject = "Overspeeding Fine Alert"

def send_mail(body,reciever_mails):
    # Set up the SMTP server
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(sender_email, app_password)
    for reciever_email in reciever_mails:
        msg=MIMEMultipart()
        msg["From"]=sender_email
        msg["To"]=reciever_email
        msg["Subject"]=subject
        msg.attach(MIMEText(body,"plain"))

        server.sendmail(sender_email,reciever_email,msg.as_string())
        print(f"Email Sent to { reciever_email }")
    server.quit()