from conference_rooms import (
    add_floor, add_room, book_room, view_user_bookings,
    list_organization_bookings_in_date_range, cancel_booking,
    search_suitable_rooms
)
from organizations import register_organization
from users import login, register_user, logout


# Function to get user input
def get_user_input(prompt):
    return input(prompt + " ").strip()


def input_to_register_organization(session_token):
    name = get_user_input('Enter your organization name: ')
    contact_info = get_user_input('Add additional contact information. Press Enter to leave blank: ')
    address = get_user_input('Add address. Press Enter to leave blank: ')

    return register_organization(
        session_token=session_token, org_name=name,
        contact_info=contact_info, address=address
    )


def input_to_register_user(session_token):
    name = get_user_input('Enter username: ')
    password1 = get_user_input('Enter password: ')
    password2 = get_user_input('Confirm password: ')

    while password1 != password2:
        print('Password do not match. Please try again')
        password1 = get_user_input('Enter password: ')
        password2 = get_user_input('Confirm password: ')

    email = get_user_input('Enter user\'s email: ')
    role = get_user_input('Enter user\'s role: ')
    permissions = get_user_input('Enter allowed permissions for the user(Separated by comma): ')
    org_id = get_user_input('Enter organization id of the user: ')

    return register_user(
        session_token=session_token, user_name=name,
        password=password1, permissions=permissions,
        role=role, email=email, org_id=org_id
    )


def input_to_add_floor(session_token):
    floor_number = get_user_input('Enter the floor number: ')
    return add_floor(
        session_token=session_token, floor_number=floor_number
    )


def input_to_add_room(session_token):
    room_number = get_user_input('Enter the room number: ')
    floor_id = get_user_input('Enter floor id: ')
    capacity = get_user_input('Enter capacity of the room: ')
    additional_details = get_user_input('Enter additional details for the room. Press Enter to leave blank: ')
    room_settings = get_user_input('Enter room seetings. Press Enter to leave blank: ')

    return add_room(
        session_token=session_token, floor_id=floor_id, room_name=room_number,
        capacity=capacity, additional_details=additional_details, room_settings=room_settings
    )


def input_to_book_room(session_token):
    room_id = get_user_input('Enter room id: ')
    start_hour = int(get_user_input('Enter the booking start time (Please make sure to follow 24-hours format): '))
    end_hour = int(get_user_input('Enter the booking end time (Please make sure to follow 24-hours format): '))
    date = get_user_input('Enter the date for which you want to book the room(Follow the format YYYY-MM-DD): ')

    return book_room(
        session_token=session_token, room_id=room_id,
        start_hour=start_hour, end_hour=end_hour, date=date
    )


def input_to_view_bookings(session_token):
    return view_user_bookings(session_token=session_token)


def input_to_list_org_bookings(session_token):
    start_date = get_user_input('Enter the start date (Format should be YYYY-MM-DD): ')
    end_date = get_user_input('Enter the end date (Format should be YYYY-MM-DD): ')

    return list_organization_bookings_in_date_range(
        session_token=session_token, start_date=start_date, end_date=end_date
    )


def input_to_cancel_booking(session_token):
    booking_id = get_user_input('Enter the booking ID: ')
    return cancel_booking(
        session_token=session_token, booking_id=booking_id
    )


def input_to_search_room(session_token):
    capacity = int(get_user_input('Enter the desired capacity: '))
    start_hour = int(get_user_input('Enter the start time (in 24 hour format): '))
    end_hour = int(get_user_input('Enter the end time (in 24 hour format): '))

    return search_suitable_rooms(
        session_token=session_token, capacity=capacity,
        start_hour=start_hour, end_hour=end_hour
    )


def input_to_logout(session_token):
    logout(session_token)
    print("Exiting the program. Goodbye!")
    raise SystemExit


# Function to display all the options
def display_options():
    menu = """
    Menu:
    1. Register Organization
    2. Register User
    3. Add Floor
    4. Add Room
    5. Book Room
    6. View Bookings
    7. List Organization Bookings in Date Range
    8. Cancel Booking
    9. Search suitable rooms
    10. Logout
    """
    print(menu)


# Define a dictionary to map user choices to functions
menu_options = {
    '1': input_to_register_organization,
    '2': input_to_register_user,
    '3': input_to_add_floor,
    '4': input_to_add_room,
    '5': input_to_book_room,
    '6': input_to_view_bookings,
    '7': input_to_list_org_bookings,
    '8': input_to_cancel_booking,
    '9': input_to_search_room,
    '10': input_to_logout
}

if __name__ == "__main__":
    session_token = login()

    if session_token:
        display_options()

        # dispay the menu until users exit
        while True:
            choice = get_user_input("Enter your choice (1-10): ")

            # Use the dictionary to execute the chosen function
            selected_function = menu_options.get(choice)
            if selected_function:
                response = selected_function(session_token=session_token)
                print(response)
            else:
                print("Invalid choice. Please select a valid option.")

            # Display the menu again
            display_options()
