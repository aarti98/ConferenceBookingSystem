import uuid
from datetime import datetime

import bcrypt

from data_structures import users, organizations, user_sessions
from validations import is_admin, is_user_registered, is_logged_in


def hash_password(password):
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password


def verify_password(hashed_password, input_password):
    return bcrypt.checkpw(input_password.encode('utf-8'), hashed_password.encode('utf-8'))


# Function to log in a user and create a session
def login():
    username = input('Enter username: ')
    password = input('Enter password: ')
    user = next((u for u in users if u["User Name"] == username), None)
    if user and verify_password(user["Password"], password):
        # Generate a unique session token
        session_token = str(uuid.uuid4())

        # Store the session data including user-related information
        session_data = {
            "user": user,
            "session_start_time": datetime.now()
        }
        user_sessions[session_token] = session_data
        return session_token  # Return the session token on successful login
    return None  # Invalid username or password


# Function to log out a user by removing their session
def logout(session_token):
    if session_token in user_sessions:
        del user_sessions[session_token]


# Function to register a new user with additional details
def register_user(session_token, org_id, user_name, password, email, role, permissions=None):
    user = is_logged_in(session_token)
    if not user:
        return "User is not logged in."
    user_id = user['User ID']
    # Check if the user is an admin
    if not is_admin(user_id):
        return "Permission denied. You are not an admin."
    # Hash the password
    hashed_password = hash_password(password)
    # Check if the username is unique
    if is_user_registered(user_name):
        return "Username is not unique. Please choose a different username."
    # Check if the organization exists
    org = next((org for org in organizations if org["Organization ID"] == org_id), None)
    if not org:
        return "Valid organization is required."
    user_id = str(uuid.uuid4())
    # Additional user details
    user_details = {
        "User ID": user_id,
        "Organization ID": org,
        "User Name": user_name,
        "Email": email,
        "Role": role,
        "Permissions": permissions.split(',') if permissions else [],
        "Password": hashed_password,  # Store the hashed password
        "Bookings": []
    }
    users.append(user_details)
    org['Users'].append(user_id)
    return "User registered successfully."
