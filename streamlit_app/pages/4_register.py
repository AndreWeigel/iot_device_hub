import streamlit as st
import requests

API_URL = "http://localhost:8000"  # Change if needed


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

def registration_page(:)
    st.title("📝 Register")

    username = st.text_input("Choose a Username")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Register"):
        # Replace with actual API call
        st.success("Registration successful! Please go to login.")
        st.page_link("account.py", label="Back to Login", icon="🔙")
