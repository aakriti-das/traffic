import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Sender credentials
sender_email = "your code@gmail.com"
app_password = "app password"  # Use Gmail App Password

# Recipient list
recipients = ["@gmail.com", "@gmail.com"]

# Email content
subject = "Test Email from Python"
body = "Hello,\nThis is a test email sent from Python script."

# Set up the SMTP server
server = smtplib.SMTP("smtp.gmail.com", 587)
server.starttls()
server.login(sender_email, app_password)

for receiver_email in recipients:
    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = receiver_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    server.sendmail(sender_email, receiver_email, msg.as_string())

server.quit()