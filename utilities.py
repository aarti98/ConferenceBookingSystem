import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from constants import SMTP_HOST, SMTP_PORT, SMTP_LOGIN_EMAIL, SMTP_PASSWORD, SENDER_EMAIL
from data_structures import organizations


def get_admin_emails(organization_name):
    organization = next((org for org in organizations if org['Name'] == organization_name), None)
    if organization:
        admin_emails = [user["Email"] for user in organization["Users"] if user.get("Role") == "Admin"]
        return admin_emails
    return "Organization not found."


def send_email(recipient_emails, subject, message):
    try:
        # Create the email message
        email = MIMEMultipart()
        email['From'] = SENDER_EMAIL
        email['Subject'] = subject
        email.attach(MIMEText(message, 'plain'))

        # Connect to the SMTP server (e.g., Gmail's SMTP server)
        server = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
        server.starttls()
        server.login(SMTP_LOGIN_EMAIL, SMTP_PASSWORD)

        for recipient_email in recipient_emails:
            email['To'] = recipient_email
            email.attach(MIMEText(message, 'plain'))

            # Send the email to the current recipient
            server.sendmail(SENDER_EMAIL, recipient_email, email.as_string())

            # Clear the recipient's email address for the next iteration
            email.replace_header('To', '')

        # Close the server connection
        server.quit()

        return "Emails sent successfully."
    except Exception as e:
        return f"Email could not be sent. Error: {str(e)}"


