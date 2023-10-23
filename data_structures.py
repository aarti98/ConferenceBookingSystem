from constants import (DEFAULT_ORG_ID, DEFAULT_USER_ID, DEFAULT_USER_NAME, DEFAULT_ORG_NAME, DEFAULT_USER_EMAIL)

# Data Structures to represent the conference room booking system
building = {
    "Floors": [],
    "Rooms": []
}

organizations = [
    {
        'Organization ID': DEFAULT_ORG_ID,
        'Name': DEFAULT_ORG_NAME,
        'Contact Information': {},
        'Address': {},
        'Users': []
    }
]
users = [
    {
        'User ID': DEFAULT_USER_ID,
        'User Name': DEFAULT_USER_NAME,
        'Email': DEFAULT_USER_EMAIL,
        "Role": 'admin',
        "Permissions": ['book'],
        "Password": '$2b$12$U6Rua/HgIe8aVXwEoYSLdOaequnEcTYsbsjGmLAtWWAu5eYq7B.PW',
        'Organization ID': DEFAULT_ORG_ID,
        "Bookings": []

    }
]

bookings = []

monthly_limits = {}

# Data structure to store global room-related settings
global_room_settings = {
    "Projector": True,
    "Seating Capacity": 50,
    "Available Amenities": ["Whiteboard", "Audio System", "Video Conferencing"],
}

# Data structure to store user sessions
user_sessions = {}
