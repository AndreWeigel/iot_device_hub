import streamlit as st
import requests

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
        st.page_link("pages/4_register.py", label="Don't have an account?")



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
        response = requests.put(f"{API_URL}/users/update", headers=headers, json=update_data)
        if response.status_code == 200:
            st.success("✅ Account updated successfully.")
        else:
            st.error(f"Failed to update: {response.json().get('detail', 'Unknown error')}")
    except Exception as e:
        st.error(f"Error: {e}")

def account():
    st.title("👤 Account Information")

    if not st.session_state.get("authenticated", False):
        st.warning("Please login first.")
        st.stop()

    token = st.session_state.get("token")
    user_info = get_user_info(token)

    if user_info:
        with st.form("update_form"):
            st.subheader("Edit Your Info")

            username = st.text_input("Username", value=user_info.get("username"))
            email = st.text_input("Email", value=user_info.get("email"))
            full_name = st.text_input("Full Name", value=user_info.get("full_name", ""))

            submitted = st.form_submit_button("Update")

            if submitted:
                update_data = {
                    "username": username,
                    "email": email,
                    "full_name": full_name
                }
                update_user_info(token, update_data)
                st.rerun()  # Refresh info after update


# Main Page
def main():
    st.set_page_config(page_title="IoT Hub", page_icon="🛠️", layout="centered")

    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.get("authenticated", False):
        login_page()
    else:
        account()

main()