import smtplib
import os
from dotenv import load_dotenv
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.message import EmailMessage
from email.header import Header
load_dotenv()
def send_html_email(sender_email,recipient_email, subject, html_content,server):
    # Create the MIME object
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = Header(subject)
    print("SUBJECT IS",subject)
    # Attach the HTML content to the email
    msg.attach(MIMEText(html_content, 'html'))

    # Set up the SMTP server
    try:
        server.send_message(msg)
        print("Email sent successfully!")
    except Exception as e:
        print(f"Error sending email: {e}")

def send_text_email(sender_email, recipient_email, subject, body,server):
    msg = EmailMessage()
    msg.set_content(body)
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = recipient_email
    server.send_message(msg)
    print("Email sent successfully.")

def get_smtp_server():
    # Example usage
 #   smtp_server = "in-v3.mailjet.com"
    smtp_server = "smtp-relay.brevo.com"
    port =587
    log_email=os.getenv("log_email_brevo").strip()
    password= os.getenv("password_brevo").strip()
    recipient_email = "tonyjacobk@gmail.com"
    sender_email="tonyjacob@hotmail.com"
    server=None
    try:
        print("Here")
        server = smtplib.SMTP(smtp_server,port)  
        server.set_debuglevel(1)
        print("server initialized")
        server.starttls()  # Secure the connection
        print ("ttls")
        server.login(log_email, password)
    except exception as e:
        print("Email Server Initialization Failed")
        return None
    return server

def send_email(subject,body,btype):
 server=get_smtp_server()
 sender_email="tonyjacob@hotmail.com"
 recipient_email="tonyjacobk@gmail.com"
 if not server:
     print("Could not connect to SMTP server ....")
     return -1
 if btype=="html":
   send_html_email(sender_email,recipient_email,subject,body,server)
 if btype=="text":
   send_text_email(sender_email,recipient_email,subject,body,server)


