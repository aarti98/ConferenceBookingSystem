import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from constants import SMTP_HOST, SMTP_PORT, SENDER_EMAIL

smtp_email = os.environ.get('SMTP_EMAIL')
smtp_password = os.environ.get('SMTP_PASSWORD')


def notify_admin_limit_exceeding(organization_name, admin_email, total_booked_hours):
    subject = f"Monthly Booking Limit Exceeded for {organization_name}"
    message = f"Dear Admin,\n\nThe organization '{organization_name}' has exceeded its monthly booking limit.\n" \
              f"Total booked hours for this month: {total_booked_hours} hours."

    try:
        # Create the email message
        email = MIMEMultipart()
        email['From'] = SENDER_EMAIL  # Your email address
        email['To'] = admin_email
        email['Subject'] = subject
        email.attach(MIMEText(message, 'plain'))

        # Connect to the SMTP server (e.g., Gmail's SMTP server)
        server = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
        server.starttls()
        server.login(smtp_email, smtp_password)

        # Send the email
        server.sendmail(smtp_email, admin_email, email.as_string())

        # Close the server connection
        server.quit()

        return "Email sent to organization admin."
    except Exception as e:
        return f"Email could not be sent. Error: {str(e)}"


# Function to notify the organization admin when the monthly limit is approaching
def notify_admin_limit_approaching(organization_name, admin_email, total_booked_hours, remaining_limit):
    subject = f"Monthly Booking Limit Approaching for {organization_name}"
    message = f"Dear Admin,\n\nThe organization '{organization_name}' is approaching its monthly booking limit.\n" \
              f"Total booked hours for this month: {total_booked_hours} hours.\n" \
              f"Remaining limit: {remaining_limit} hours."

    try:
        # Create the email message
        email = MIMEMultipart()
        email['From'] = 'your_email@gmail.com'  # Your email address
        email['To'] = admin_email
        email['Subject'] = subject
        email.attach(MIMEText(message, 'plain'))

        # Connect to the SMTP server (e.g., Gmail's SMTP server)
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login('your_email@gmail.com', 'your_application_specific_password')

        # Send the email
        server.sendmail('your_email@gmail.com', admin_email, email.as_string())

        # Close the server connection
        server.quit()

        return "Email sent to organization admin."
    except Exception as e:
        return f"Email could not be sent. Error: {str(e)}"
