import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from create_logreport import get_report
def send_html_email(log_email, password, recipient_email, subject, html_file_path):
    # Create the MIME object
    msg = MIMEMultipart()
    msg['From'] = "tonyjacob@hotmail.com"
    msg['To'] = recipient_email
    msg['Subject'] = subject
    """
    # Read the HTML file
    try:
        with open(html_file_path, 'r', encoding='utf-8') as file:
            html_content = file.read()
    except FileNotFoundError:
        print(f"Error: The file {html_file_path} was not found.")
        return
    except Exception as e:
        print(f"Error reading HTML file: {e}")
        return
    """
    html_content=get_report()
    # Attach the HTML content to the email
    msg.attach(MIMEText(html_content, 'html'))

    # Set up the SMTP server
    try:
        server = smtplib.SMTP(smtp_server,port)  # Using Gmail SMTP server
        server.starttls()  # Enable TLS
        server.login(log_email, password)
        print("logged") 
        # Send the email
        server.send_message(msg)
        print("Email sent successfully!")
        
        # Close the server connection
        server.quit()
    except Exception as e:
        print(f"Error sending email: {e}")

if __name__ == "__main__":
    # Example usage
    smtp_server = "in-v3.mailjet.com"
    port =587
    log_email = "4c1f5307575c5bf397b35db5348767b1"
    password = "f623b20bfb0b61507edc6ed3ff832e07"  # 🔑 replace with your actual password
    recipient_email = "tonyjacobk@gmail.com"
    sender_email="tonyjacob@hotmail.com"

    subject = "HTML Email Test"
    html_file_path = "report_summary.html"  # Replace with your HTML file path

    send_html_email(log_email, password, recipient_email, subject, html_file_path)
