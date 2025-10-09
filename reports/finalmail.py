import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.message import EmailMessage
from create_logreport import get_report
from errmail import create_error_report
def send_html_email(log_email, password, recipient_email, subject, html_content,server):
    # Create the MIME object
    msg = MIMEMultipart()
    msg['From'] = "tonyjacob@hotmail.com"
    msg['To'] = recipient_email
    msg['Subject'] = subject
    # Attach the HTML content to the email
    msg.attach(MIMEText(html_content, 'html'))

    # Set up the SMTP server
    try:
        server.send_message(msg)
        print("Email sent successfully!")
    except Exception as e:
        print(f"Error sending email: {e}")

def send_text_email(smtp_server, port, sender_email,password , recipient_email, subject, body,server):
    msg = EmailMessage()
    msg.set_content(body)
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = recipient_email
    server.send_message(msg)
    print("Email sent successfully.")

if __name__ == "__main__":
    # Example usage
    smtp_server = "in-v3.mailjet.com"
    port =587
    log_email = "4c1f5307575c5bf397b35db5348767b1"
    password = "f623b20bfb0b61507edc6ed3ff832e07"  # 🔑 replace with your actual password
    recipient_email = "tonyjacobk@gmail.com"
    sender_email="tonyjacob@hotmail.com"
    try:
        server = smtplib.SMTP(smtp_server,port)  
        server.starttls()  # Secure the connection
        print ("ttls")
        server.login(log_email, password)
        print("Logged")
        subject = "HTML Email Test"
        html_file_path = "report_summary.html"  # Replace with your HTML file path
        html_content=get_report()
        send_html_email(log_email, password, recipient_email, subject, html_content,server)
        subject="Error and Exception report"
        html_content=create_error_report()
        send_text_email(smtp_server,port,sender_email, password, recipient_email, subject, html_content,server)
        server.quit()
    except Exception as e :    
       print(f"Error sending email: {e}")

