import streamlit as st
import pandas as pd
import os
import time

# File to store user data
USER_DATA_FILE = 'user_data.csv'

# Initialize session state for login status and user data
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# Load user data from CSV
if os.path.exists(USER_DATA_FILE):
    user_data = pd.read_csv(USER_DATA_FILE)
    st.session_state.users = {row['Username']: row.to_dict() for index, row in user_data.iterrows()}
else:
    st.session_state.users = {}

# Set pastel background color
st.markdown(
    """
    <style>
    body {
        background-color: #31333F;  /* Example pastel color */
    }
    </style>
    """,
    unsafe_allow_html=True
)


def add_user(username, details):
    if username in st.session_state.users:
        return "error: Username already exists"
    
    st.session_state.users[username] = details
    save_users()
    return f"success: User {username} registered successfully!"

def login():
    st.write("### :rainbow[Log in]")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Log in"):
        if username in st.session_state.users and st.session_state.users[username]['Password'] == password:
            st.session_state.logged_in = True
            st.success("Logged in successfully!")
            st.rerun()
        else:
            st.error("Invalid credentials")

def logout():
    if st.button("Log out"):
        st.session_state.logged_in = False
        st.success("Logged out successfully!")
        st.rerun()

def register():
    st.header(":rainbow[Register New User]")
    if "show_extra_info_form" not in st.session_state:
        st.session_state.show_extra_info_form = False

    if not st.session_state.show_extra_info_form:
        # Basic Info Form
        with st.form("basic_info_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            next_button = st.form_submit_button("Next")

            if next_button:
                if username and password:
                    st.session_state.username = username
                    st.session_state.password = password
                    st.session_state.show_extra_info_form = True
                else:
                    st.warning("Please fill out both fields.")
    else:
        # Additional Info Form
        with st.form("additional_info_form"):
            user_type = st.selectbox("User Type", ["Retailer", "Wholesaler", "Distributor"])
            first_name = st.text_input("First Name")
            last_name = st.text_input("Last Name")
            date_of_birth = st.date_input("Date of Birth")
            gender = st.selectbox("Gender", ["Male", "Female", "Other"])
            email = st.text_input("Email")
            phone_number = st.text_input("Phone Number")
            address = st.text_input("Address")
            city = st.text_input("City")
            state = st.text_input("State")
            postal_code = st.text_input("Postal Code")
            aadhaar_number = st.text_input("Aadhaar Number")
            pan_number = st.text_input("PAN Number")
            register_button = st.form_submit_button("Register")

            if register_button:
                if all([first_name, last_name, email, phone_number, address, city, state, postal_code, aadhaar_number, pan_number]):
                    details = {
                        "Username": st.session_state.username,
                        "Password": st.session_state.password,
                        "User Type": user_type,
                        "First Name": first_name,
                        "Last Name": last_name,
                        "Date of Birth": date_of_birth,
                        "Gender": gender,
                        "Email": email,
                        "Phone Number": phone_number,
                        "Address": address,
                        "City": city,
                        "State": state,
                        "Postal Code": postal_code,
                        "Aadhaar Number": aadhaar_number,
                        "PAN Number": pan_number,
                        "Registration Date": pd.to_datetime('today').date()
                    }
                    result = add_user(st.session_state.username, details)

                    if result.startswith("success"):
                        st.success(result.split(": ")[1])
                        # Show progress bar
                        progress_bar = st.progress(0)
                        for i in range(100):
                            progress_bar.progress(i + 1)
                            time.sleep(0.05)  # Simulating some processing time
                    else:
                        st.error(result.split(": ")[1])

                    st.session_state.show_extra_info_form = False  # Reset for next registration
                else:
                    st.warning("Please fill out all additional fields.")

def reset_password():
    if "username_to_reset" not in st.session_state:
        st.session_state.username_to_reset = ""

    username = st.text_input("Enter your username to reset password", value=st.session_state.username_to_reset)
    new_password = st.text_input("Enter new password", type="password")
    
    if st.button("Reset Password"):
        if username in st.session_state.users:
            st.session_state.users[username]['Password'] = new_password
            save_users()
            st.success("Password reset successfully!")
            st.session_state.username_to_reset = ""  # Clear the username input
        else:
            st.error("Username not found")

def save_users():
    # Save user data to CSV
    user_data = pd.DataFrame.from_records(list(st.session_state.users.values()))  # Convert to list of records
    user_data.to_csv(USER_DATA_FILE, index=False)

def plot_user_growth():
    user_data = pd.DataFrame.from_records(list(st.session_state.users.values()))
    user_data['Registration Date'] = pd.to_datetime(user_data['Registration Date'])
    
    # Group by month and count users
    monthly_users = user_data.resample('M', on='Registration Date').size().reset_index(name='User Count')
    
    st.line_chart(monthly_users.set_index('Registration Date'))

def home():
    st.write("### :rainbow[Registered Users]")
    if st.session_state.users:
        user_list = pd.DataFrame.from_records(list(st.session_state.users.values()))  # Convert to list of records
        st.dataframe(user_list)
        
        st.write("### :rainbow[User Growth Over Time]")
        plot_user_growth()  # Plotting user growth
    else:
        st.write("No registered users.")

# Define pages for navigation
login_page = st.Page(login, title="Log in", icon=":material/login:")
logout_page = st.Page(logout, title="Log out", icon=":material/logout:")
register_page = st.Page(register, title="Register", icon=":material/app_registration:")
reset_password_page = st.Page(reset_password, title="Reset Password", icon=":material/password:")
home_page = st.Page(home, title="Home", icon=":material/home:")

# Navigation logic based on login status
if st.session_state.logged_in:
    pg = st.navigation(
        {
            "Home": home_page,
            "Account": [logout_page, reset_password_page],
        }
    )
else:
    pg = st.navigation([home_page, login_page, register_page])

pg.run()
