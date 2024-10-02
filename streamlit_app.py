import streamlit as st
import pandas as pd
import os
import time
from datetime import datetime, timedelta

# File to store user data
USER_DATA_FILE = 'user_data.csv'
SESSION_TIMEOUT = timedelta(minutes=15)  # Set session timeout duration

# Initialize session state for login status, user data, and active sessions
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "last_activity" not in st.session_state:
    st.session_state.last_activity = datetime.now()
if "login_attempts" not in st.session_state:
    st.session_state.login_attempts = 0
if "users" not in st.session_state:
    st.session_state.users = {}
if "confirm_logout" not in st.session_state:
    st.session_state.confirm_logout = False  # State for logout confirmation

# Load user data from CSV
if os.path.exists(USER_DATA_FILE):
    user_data = pd.read_csv(USER_DATA_FILE)
    st.session_state.users = {row['Username']: row.to_dict() for index, row in user_data.iterrows()}

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

def check_session():
    if datetime.now() - st.session_state.last_activity > SESSION_TIMEOUT:
        st.session_state.logged_in = False
        st.warning("Your session has timed out. Please log in again.")
        st.rerun()

def login():
    check_session()
    st.write("### :rainbow[Log in]")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Log in"):
        if username in st.session_state.users and st.session_state.users[username]['Password'] == password:
            st.session_state.logged_in = True
            st.session_state.current_user = username
            st.session_state.last_activity = datetime.now()  # Reset activity time
            st.success("Logged in successfully!")
            st.session_state.login_attempts = 0  # Reset failed attempts
            st.rerun()
        else:
            st.session_state.login_attempts += 1
            st.error("Invalid credentials")
            if st.session_state.login_attempts >= 3:
                st.warning("Too many failed attempts. Please try again later.")

def logout():
    st.session_state.logged_in = False
    st.success("Logged out successfully!")
    st.rerun()

def register():
    st.header(":rainbow[Register New User]")
    if "show_extra_info_form" not in st.session_state:
        st.session_state.show_extra_info_form = False

    if not st.session_state.show_extra_info_form:
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
                        progress_bar = st.progress(0)
                        for i in range(100):
                            progress_bar.progress(i + 1)
                            time.sleep(0.05)
                    else:
                        st.error(result.split(": ")[1])

                    st.session_state.show_extra_info_form = False
                else:
                    st.warning("Please fill out all additional fields.")

def reset_password():
    username = st.text_input("Enter your username to reset password")
    new_password = st.text_input("Enter new password", type="password")
    
    if st.button("Reset Password"):
        if username in st.session_state.users:
            st.session_state.users[username]['Password'] = new_password
            save_users()
            st.success("Password reset successfully!")
        else:
            st.error("Username not found")

def save_users():
    user_data = pd.DataFrame.from_records(list(st.session_state.users.values()))
    user_data.to_csv(USER_DATA_FILE, index=False)

def plot_user_growth():
    user_data = pd.DataFrame.from_records(list(st.session_state.users.values()))
    user_data['Registration Date'] = pd.to_datetime(user_data['Registration Date'])
    
    monthly_users = user_data.resample('M', on='Registration Date').size().reset_index(name='User Count')
    
    st.line_chart(monthly_users.set_index('Registration Date'))

def home():
    check_session()
    # st.title(f"You are at the right place, **{st.session_state.current_user}**!")
    st.write("### :rainbow[Registered Users]")
    if st.session_state.users:
        # st.write(f"You are at the right place, **{st.session_state.current_user}**!")
        user_list = pd.DataFrame.from_records(list(st.session_state.users.values()))
        st.dataframe(user_list)
        
        st.write("### :rainbow[User Growth Over Time]")
        plot_user_growth()
    else:
        st.write("No registered users.")

def settings_page():
    st.header(":rainbow[Settings]")
    
    email_notifications = st.checkbox("Email Notifications", value=True)
    sms_notifications = st.checkbox("SMS Notifications", value=False)
    
    languages = ["English", "Spanish", "French", "German", "Chinese"]
    selected_language = st.selectbox("Select Language", languages)

    data_sharing = st.selectbox("Data Sharing Preferences", ["Allow", "Do Not Allow"])

    if st.button("Save Settings"):
        st.session_state.users[st.session_state.current_user]['Preferences'] = {
            "Email Notifications": email_notifications,
            "SMS Notifications": sms_notifications,
            "Language": selected_language,
            "Data Sharing": data_sharing
        }
        save_users()
        st.success("Settings saved successfully!")

def edit_user_info():
    st.header(":rainbow[Edit User Information]")
    current_user = st.session_state.current_user
    user_info = st.session_state.users[current_user]

    with st.form("edit_user_form"):
        first_name = st.text_input("First Name", user_info['First Name'])
        last_name = st.text_input("Last Name", user_info['Last Name'])
        email = st.text_input("Email", user_info['Email'])
        phone_number = st.text_input("Phone Number", user_info['Phone Number'])
        address = st.text_input("Address", user_info['Address'])
        city = st.text_input("City", user_info['City'])
        state = st.text_input("State", user_info['State'])
        postal_code = st.text_input("Postal Code", user_info['Postal Code'])
        update_button = st.form_submit_button("Update")

        if update_button:
            user_info.update({
                "First Name": first_name,
                "Last Name": last_name,
                "Email": email,
                "Phone Number": phone_number,
                "Address": address,
                "City": city,
                "State": state,
                "Postal Code": postal_code,
            })
            save_users()
            st.success("User information updated successfully!")

def delete_account():
    st.header(":rainbow[Delete Account]")
    current_user = st.session_state.current_user
    if st.button("Delete My Account"):
        del st.session_state.users[current_user]
        save_users()
        st.success("Account deleted successfully!")
        st.session_state.logged_in = False
        st.rerun()

def export_user_data():
    st.header(":rainbow[Export User Data]")
    if st.button("Export User Data"):
        user_data = pd.DataFrame.from_records(list(st.session_state.users.values()))
        csv = user_data.to_csv(index=False)
        st.download_button("Download CSV", csv, "user_data.csv", "text/csv")

def import_user_data():
    st.header(":rainbow[Import User Data]")
    uploaded_file = st.file_uploader("Upload CSV", type="csv")
    
    if uploaded_file is not None:
        data = pd.read_csv(uploaded_file)
        for index, row in data.iterrows():
            username = row['Username']
            if username not in st.session_state.users:
                st.session_state.users[username] = row.to_dict()
        save_users()
        st.success("User data imported successfully!")

# Check session before displaying the main app
check_session()

if st.session_state.logged_in:
    # Display a personalized welcome message
    # st.sidebar.markdown(f"### You are at the right place, **{st.session_state.current_user}**!")

    # st.sidebar.markdown(f"### You are at the right place, **{st.session_state.current_user}**!")
    pg = st.sidebar.radio("Hello", [
        "🏠 Home",
        "📥 Import User Data",
        "📊 Export User Data",
        "✏️ Edit User Info",
        "🔄 Reset Password",
        "🗑️ Delete Account",
        "⚙️ Settings",
        "🔑 Log out"
    ])
    
    if pg == "🏠 Home":
        home()
    elif pg == "🔄 Reset Password":
        reset_password()
    elif pg == "⚙️ Settings":
        settings_page()
    elif pg == "✏️ Edit User Info":
        edit_user_info()
    elif pg == "🗑️ Delete Account":
        delete_account()
    elif pg == "📊 Export User Data":
        export_user_data()
    elif pg == "📥 Import User Data":
        import_user_data()
    
    elif pg == "🔑 Log out":
        if st.session_state.get("confirm_logout", False):
            if st.popover("Confirm Logout"):
                logout()  # Log out if confirmed
        else:
            if st.button("Log out"):
                st.session_state.confirm_logout = True
                st.warning("Are you sure you want to log out?")
else:
    st.sidebar.markdown("### Navigation")
    pg = st.sidebar.radio("Welcome", [
        "🏠 Home",
        "🔑 Log in",
        "📝 Register"
    ])
    
    if pg == "🏠 Home":
        home()
    elif pg == "🔑 Log in":
        login()
    elif pg == "📝 Register":
        register()
