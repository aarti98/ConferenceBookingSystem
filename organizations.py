import uuid
import threading

from data_structures import organizations
from utilities import send_email
from validations import is_admin, is_organization_registered, is_logged_in


# Function to register a new organization
def register_organization(session_token, org_name, contact_info=None, address=None):
    # Check if the user is logged in and is an admin
    user = is_logged_in(session_token)
    if not user:
        return 'User is not logged in.'
    user_id = user['User ID']
    # Check if the user is an admin
    if not is_admin(user_id):
        return "Permission denied. You are not an admin."
    # Check if the organization name is unique
    if is_organization_registered(org_name):
        return "Organization name is not unique. Please choose a different name."
    # Generate a unique ID for the floor
    org_id = str(uuid.uuid4())
    # Additional organization details
    org_details = {
        "Organization ID": org_id,
        "Organization Name": org_name,
        "Contact Information": contact_info or {},
        "Address": address or {},
        "Users": []
    }

    organizations.append(org_details)
    return "Organization registered successfully."


def notify_admins_limit_exceeding(organization_name, admin_emails, total_booked_hours):
    subject = f"Monthly Booking Limit Exceeded for {organization_name}"
    message = f"Dear Admin,\n\nThe organization '{organization_name}' has exceeded its monthly booking limit.\n" \
              f"Total booked hours for this month: {total_booked_hours} hours."

    email_thread = threading.Thread(target=send_email, args=(admin_emails, subject, message))
    email_thread.start()


# Function to notify the organization admin when the monthly limit is approaching
def notify_admins_limit_approaching(organization_name, admin_emails, total_booked_hours, remaining_limit):
    subject = f"Monthly Booking Limit Approaching for {organization_name}"
    message = f"Dear Admin,\n\nThe organization '{organization_name}' is approaching its monthly booking limit.\n" \
              f"Total booked hours for this month: {total_booked_hours} hours.\n" \
              f"Remaining limit: {remaining_limit} hours."

    email_thread = threading.Thread(target=send_email, args=(admin_emails, subject, message))
    email_thread.start()
