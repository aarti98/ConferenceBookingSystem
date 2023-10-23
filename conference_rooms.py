import threading
import uuid
from datetime import datetime as dt

from data_structures import building, global_room_settings, organizations, users
from organizations import notify_admins_limit_approaching, notify_admins_limit_exceeding
from utilities import get_admin_emails
from validations import is_admin, is_logged_in, is_organization_registered

# Create a lock for concurrent access to the 'building' data structure
building_lock = threading.Lock()


# Function to add a new floor with admin and logged-in user checks
def add_floor(session_token, floor_number):
    # Check if the user is logged in and is an admin
    user = is_logged_in(session_token)
    if not user:
        return "User is not logged in."
    user_id = user['User ID']
    if not is_admin(user_id):
        return "Permission denied. You are not an admin."

    floor_id = str(uuid.uuid4())

    # Check if the floor number is already taken
    if any(floor["Floor Number"] == floor_number for floor in building["Floors"]):
        return "Floor number already exists."

    # Create a new floor
    new_floor = {
        "Floor ID": floor_id,
        "Floor Number": floor_number,
        "Room IDs": []
    }

    building["Floors"].append(new_floor)

    return f"Floor '{floor_number}' added with Floor ID: {floor_id} successfully."


# Function to add a new room to an existing floor
def add_room(session_token, floor_id, room_name, capacity, additional_details=None, room_settings=None):
    # Check if the user is logged in
    user = is_logged_in(session_token)
    if not user:
        return "User is not logged in."
    user_id = user['User ID']
    # check if user is admin
    if not is_admin(user_id):
        return "Permission denied. You are not an admin."

    # Check if the floor exists
    floor = next((f for f in building["Floors"] if f["Floor ID"] == floor_id), None)
    if not floor:
        return "Floor not found."

    # Generate a unique room ID
    room_id = str(uuid.uuid4())
    # Check if the room name is already taken on this floor
    if any(room["Room Name"] == room_name for room in building["Rooms"]):
        return "Room name already exists on this floor."

    # Create a new room
    new_room = {
        "Room ID": room_id,
        "Room Name": room_name,
        "Capacity": capacity,
        "Additional Details": additional_details or {},
        "Availability": [0] * 24,  # Initialize availability for all hours,
        "Room Settings": room_settings or global_room_settings
    }

    building["Rooms"].append(new_room)
    floor['Room IDs'].append(room_id)
    return f"Room '{room_name}' added with Room ID: {room_id} to Floor with Floor ID: {floor_id} successfully."


# 6. Book Room
def book_room(session_token, room_id, start_hour, end_hour, date):
    # Check if the user is logged in
    user = is_logged_in(session_token)
    if not user:
        return "User is not logged in."

    # Parse the date string into a datetime object
    date_obj = dt.strptime(date, "%Y-%m-%d")
    room = None
    for room in building['Rooms']:
        if room['Room ID'] == room_id:
            break

    if room is None:
        return "Room not found."

    # Lock the 'building' data structure to prevent concurrent access
    with building_lock:
        room_availability = room["Availability"]

        # Check if the room is available during the requested time slot
        for hour in range(start_hour, end_hour):
            if room_availability[hour] != 0:
                return "Room is not available at the requested time."

        # Check if the user has the necessary permissions
        if "book" not in user["Permissions"]:
            return "Permission denied. You do not have the necessary permissions."

        booking_duration = end_hour - start_hour

        for org in organizations:
            if org['Organization ID'] == user['Organization ID']:
                organization = org
                break
        # Calculate the organization's total monthly booked hours
        organization_monthly_booked_hours = sum(
            booking["End Hour"] - booking["Start Hour"]
            for user_id in organization.get("Users", [])
            for user in users if user['User ID'] == user_id
            for booking in user.get("Bookings", [])
            if booking.get("Month") == date_obj.month
        )

        # Calculate the remaining monthly limit for the organization
        remaining_monthly_limit = 30 - organization_monthly_booked_hours

        if booking_duration >= remaining_monthly_limit:
            return "Organization has exceeded the monthly booking limit."

        # If all checks pass, update the room availability and add the booking
        # Generate a unique booking ID
        booking_id = str(uuid.uuid4())
        for hour in range(start_hour, end_hour):
            room_availability[hour] = 1

        user["Bookings"].append({
            "Booking ID": booking_id,
            "Date": date,
            "Room ID": room_id,
            "Start Hour": start_hour,
            "End Hour": end_hour
        })
        admin_emails = get_admin_emails(organization['Name'])
        # Notify the organization if approaching/exceeding the monthly limit
        if remaining_monthly_limit <= 0:
            notify_admins_limit_exceeding(
                organization['Name'], admin_emails, organization_monthly_booked_hours
            )
        elif remaining_monthly_limit <= 10:
            notify_admins_limit_approaching(
                organization['Name'], admin_emails, organization_monthly_booked_hours, remaining_monthly_limit
            )

        return "Booking confirmed."


# Function to check if a booking can be canceled (e.g., based on time difference)
def can_cancel_booking(booking):
    # Implement your criteria for cancellation, e.g., notice period
    current_time = dt.now()
    booking_start_time = current_time.replace(hour=booking["Start Hour"], minute=0, second=0, microsecond=0)
    time_difference = booking_start_time - current_time
    return time_difference.total_seconds() >= 900  # 900 seconds = 15 minutes


# Function to cancel a booking with time-based checks
def cancel_booking(session_token, booking_id):
    # Check if the user is logged in
    logged_in_user = is_logged_in(session_token)
    if not logged_in_user:
        return "User is not logged in."
    user = logged_in_user

    org = is_organization_registered(user['Organization ID'])

    # Find the booking by its booking ID
    booking_to_cancel = None
    for booking in user["Bookings"]:
        if booking.get("Booking ID") == booking_id:
            booking_to_cancel = booking
            break
    if not booking_to_cancel:
        return "Booking not found."

    # Check if the booking can be canceled (based on time difference or other criteria)
    if not can_cancel_booking(booking_to_cancel):
        return "Booking cannot be canceled."

    # Update room availability and remove the booking
    floor_name = booking_to_cancel.get("Floor")
    room_name = booking_to_cancel.get("Room")
    start_hour = booking_to_cancel.get("Start Hour")
    end_hour = booking_to_cancel.get("End Hour")

    room_availability = building["Floors"][floor_name][room_name]["Availability"]
    for hour in range(start_hour, end_hour):
        room_availability[hour] = 0
    user["Bookings"].remove(booking_to_cancel)

    # Update the organization's monthly booking hours accordingly
    org["Monthly Booked Hours"] -= (end_hour - start_hour)

    return "Booking cancelled successfully."


# Function to view a user's current and past bookings
def view_user_bookings(session_token):
    # Check if the user is logged in
    logged_in_user = is_logged_in(session_token)
    if not logged_in_user:
        return "User is not logged in."

    user = logged_in_user

    # Retrieve the user's booking history
    user_bookings = user.get("Bookings", [])

    # Separate bookings into current and past based on the current time
    current_time = dt.now()
    current_date = current_time.date()

    current_bookings = []
    past_bookings = []
    for booking in user_bookings:
        booking_date = dt.strptime(booking['date'], "%Y-%m-%d")
        booking_start_time = current_time.replace(hour=booking["Start Hour"], minute=0, second=0, microsecond=0)
        if booking_date > current_date and booking_start_time > current_time:
            current_bookings.append(booking)
        else:
            past_bookings.append(booking)

    return {
        "Current Bookings": current_bookings,
        "Past Bookings": past_bookings
    }


# Function to list all organization bookings in a date range
def list_organization_bookings_in_date_range(session_token, start_date, end_date):
    # Check if the user is logged in
    logged_in_user = is_logged_in(session_token)
    if not logged_in_user:
        return "User is not logged in."

    user = logged_in_user
    # Retrieve the user's organization name
    organization_id = user.get("Organization ID")
    for org in organizations:
        if org['Organization ID'] == organization_id:
            organization = org
            break
    # Create a list to store relevant bookings
    relevant_bookings = []

    org_users = [user for user in users if user['Organization ID'] == organization_id]
    # Iterate through all users of the organization
    for user in org_users:
        user_bookings = user.get("Bookings", [])
        for booking in user_bookings:
            date_obj = dt.strptime(booking['Date'], "%Y-%m-%d")
            start_date = dt.strptime(start_date, "%Y-%m-%d")
            end_date = dt.strptime(end_date, "%Y-%m-%d")
            if start_date <= date_obj <= end_date:
                relevant_bookings.append(booking)

    return relevant_bookings


def search_suitable_rooms(session_token, capacity, start_hour, end_hour):
    # Check if the user is logged in
    logged_in_user = is_logged_in(session_token)
    if not logged_in_user:
        return "User is not logged in."

    suitable_rooms = []

    for floor_name, floor in building["Floors"].items():
        for room_name, room in floor["Rooms"].items():
            room_capacity = room["Capacity"]
            availability = room["Availability"][start_hour:end_hour]

            if room_capacity >= capacity and all(availability):
                suitable_rooms.append((floor_name, room_name))

    return suitable_rooms
