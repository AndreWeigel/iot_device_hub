import streamlit as st
import requests
from datetime import datetime
import time

API_URL = "http://localhost:8000"  # Change if needed


def login(username, password):
    data = {
        "username": username,
        "password": password,
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    try:
        response = requests.post(f"{API_URL}/token", data=data, headers=headers)
        if response.status_code == 200:
            return response.json()  # {'access_token': '...', 'token_type': 'bearer'}
        else:
            return None
    except Exception as e:
        st.error(f"Login failed: {e}")
        return None


def login_page():
    st.title("🔐 Login")

    st.set_page_config(
        page_title="Login Page",   # Browser tab title
        page_icon="🔐"
    )

    if st.session_state.authenticated:
        st.success("You are logged in!")
        st.page_link("pages/1_dashboard.py", label="Go to Dashboard")
    else:
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            auth = login(username, password)
            if auth:
                st.session_state.authenticated = True
                st.session_state.token = auth["access_token"]
                st.session_state.user_id = username
                st.rerun()
            else:
                st.error("Invalid credentials")



def register(username, email, password):
    data = {
        "username": username,
        "email": email,
        "password": password
    }
    try:
        response = requests.post(f"{API_URL}/register", json=data)
        if response.status_code == 201:
            return response.json()
        else:
            st.error(f"Registration failed: {response.json().get('detail')}")
            return None
    except Exception as e:
        st.error(f"Registration error: {e}")
        return None


def registration_page():
    st.title("📝 Register")

    username = st.text_input("Choose a Username")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Register"):
        # Replace with actual API call
        st.success("Registration successful! Please go to login.")
        st.page_link("account.py", label="Back to Login", icon="🔙")


def get_user_info(token):
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.get(f"{API_URL}/user", headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            st.error("Failed to load user info.")
            return None
    except Exception as e:
        st.error(f"Error: {e}")
        return None


def update_user_info(token, update_data):
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    try:
        response = requests.put(f"{API_URL}/user", headers=headers, json=update_data)

        if response.status_code == 200:
            return True  # Let the caller handle success message
        else:
            error_msg = response.json().get('detail', 'Unknown error')
            st.error(f"Failed to update: {error_msg}")
            return False

    except requests.exceptions.RequestException as e:
        st.error(f"Network error: {e}")
        return False


def change_password(token, old_password, new_password, confirm_password):
    url = f"{API_URL}/user/password"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    payload = {
        "old_password": old_password,
        "new_password": new_password,
        "new_password_confirm": confirm_password
    }

    try:
        response = requests.post(url, headers=headers, json=payload)

        if response.status_code == 204:
            return True
        else:
            error_msg = response.json().get("detail", "Unknown error")
            st.error(f"Failed to change password: {error_msg}")
            return False

    except requests.exceptions.RequestException as e:
        st.error(f"Network error: {e}")
        return False


def format_date(date_str):
    try:
        dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        suffix = lambda d: "th" if 11 <= d <= 13 else {1: "st", 2: "nd", 3: "rd"}.get(d % 10, "th")
        return f"{dt.day}{suffix(dt.day)} of {dt.strftime('%B %Y')}"
    except Exception:
        return "—"




def account():

    st.title("👤 Account Information")

    if not st.session_state.get("authenticated", False):
        st.warning("Please login first.")
        st.stop()

    token = st.session_state.get("token")
    user_info = get_user_info(token)

    if user_info:
        st.divider()

        # --- User Info ---

        st.markdown(f"👤 **Username:** {user_info.get('username', '—')}")
        st.markdown(f"📧 **Email:** {user_info.get('email', '—')}")

        created_at = user_info.get('created_at')
        formatted_date = format_date(created_at) if created_at else "—"
        st.markdown(f"📅 **Created at:** {formatted_date}")

        status = user_info.get("is_active", True)
        status_text = "🟢 Active" if status else "🔴 Inactive"
        st.markdown(f"🔐 **Status:** {status_text}")

        st.divider()

        # --- Update Info Section ---
        with st.expander("✏️ Update User Info", expanded=False):
            with st.form("update_user_info"):
                new_username = st.text_input("Username", value=user_info["username"])
                new_email = st.text_input("Email", value=user_info["email"])
                submit_update = st.form_submit_button("Update Info")

                if submit_update:
                    user_payload = {
                        "username": new_username,
                        "email": new_email
                    }
                    success = update_user_info(token, user_payload)
                    if success:
                        st.success("✅ User info updated.")
                        time.sleep(2)
                        st.rerun()

        # --- Change Password Section ---
        with st.expander("🔒 Change Password", expanded=False):
            with st.form("change_password"):
                current_pw = st.text_input("Current Password", type="password")
                new_pw = st.text_input("New Password", type="password")
                confirm_pw = st.text_input("Confirm New Password", type="password")
                submit_pw = st.form_submit_button("Change Password")

                if submit_pw:
                    if new_pw != confirm_pw:
                        st.error("New passwords do not match.")
                    else:
                        success = change_password(token, current_pw, new_pw, confirm_pw)
                        if success:
                            st.success("✅ Password changed successfully.")
                            time.sleep(2)
                            st.rerun()

        st.divider()


# Main Page
def main():
    st.set_page_config(page_title="IoT Hub", page_icon="🛠️", layout="centered")

    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.get("authenticated", False):

        mode = st.radio(
            "Select action",
            ["Log in", "Create account"],
            horizontal=True,
            label_visibility="collapsed"  # hide the label so only the buttons show
        )
        if mode == "Log in":
            login_page()
        else:
            registration_page()
    else:
        account()

main()