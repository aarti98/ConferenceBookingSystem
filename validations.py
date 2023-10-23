from datetime import datetime, timedelta

from data_structures import users, organizations, user_sessions

# Session timeout duration (e.g., 30 minutes)
session_timeout = timedelta(minutes=30)


# generalised function to check admin users
def is_admin(user_id):
    user = next((user for user in users if user['User ID'] == user_id), None)
    return user and user["Role"] == "admin"


# Function to check if an organization is already registered
def is_organization_registered(org_name):
    return any(org["Name"] == org_name for org in organizations)


# Function to check if a user is already registered
def is_user_registered(user_name):
    return any(user["User Name"] == user_name for user in users)


# Function to check if a user is logged in and return the user object
def is_logged_in(session_token):
    if session_token in user_sessions:
        session_data = user_sessions[session_token]
        session_start_time = session_data["session_start_time"]
        current_time = datetime.now()

        # Check if the session has timed out
        if current_time - session_start_time <= session_timeout:
            return session_data["user"]  # Return the user object if logged in
        else:
            del user_sessions[session_token]  # Remove the expired session
    return None  # User is not logged in


def has_necessary_permissions(user, permission):
    if permission in user['Permissions']:
        return True
    return False
