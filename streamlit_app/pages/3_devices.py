import streamlit as st
import requests

API_BASE_URL = "http://localhost:8000"  # Replace with your API URL
ACCESS_TOKEN = "your_token_here"  # Paste your JWT token here or load from a secure source

token = st.session_state.get("token")
headers = {"Authorization": f"Bearer {token}"} if token else {}

st.set_page_config(page_title="Device Manager", layout="wide")
st.title("📟 Device Management")

# --- Helper functions ---
def fetch_devices():
    response = requests.get(f"{API_BASE_URL}/device", headers=headers)
    return response.json() if response.status_code == 200 else []

def update_device(device_id, name):
    payload = {"name": name}
    return requests.put(f"{API_BASE_URL}/devices/{device_id}", json=payload, headers=headers)

def delete_device(device_id):
    return requests.delete(f"{API_BASE_URL}/devices/{device_id}", headers=headers)

def toggle_mqtt(device_id, enabled):
    return requests.put(
        f"{API_BASE_URL}/devices/{device_id}/mqtt",
        params={"mqtt_enabled": enabled},
        headers=headers
    )

def create_device(payload):
    return requests.post(f"{API_BASE_URL}/device", json=payload, headers=headers)

# --- Device List Display ---
st.subheader("🔧 Your Devices")
devices = fetch_devices()

if devices:
    for device in devices:
        with st.expander(f"Device: {device['name']} (ID: {device['id']})"):
            col1, col2, col3 = st.columns([3, 1, 1])

            with col1:
                updated_name = st.text_input("Device Name", value=device["name"], key=f"name_{device['id']}")
            with col2:
                if st.button("💾 Update", key=f"update_{device['id']}"):
                    res = update_device(device["id"], updated_name)
                    if res.status_code == 200:
                        st.success("Updated successfully!")
                    else:
                        st.error("Update failed.")
            with col3:
                if st.button("🗑️ Delete", key=f"delete_{device['id']}"):
                    res = delete_device(device["id"])
                    if res.status_code == 204:
                        st.success("Deleted!")
                    else:
                        st.error("Delete failed.")

            mqtt_col, _ = st.columns([1, 5])
            with mqtt_col:
                current_mqtt = device.get("mqtt_enabled", False)
                mqtt_toggle = st.toggle("MQTT", value=current_mqtt, key=f"mqtt_{device['id']}")
                if st.button("🔄 Apply MQTT", key=f"mqtt_apply_{device['id']}"):
                    res = toggle_mqtt(device["id"], mqtt_toggle)
                    if res.status_code == 200:
                        st.success("MQTT updated!")
                    else:
                        st.error("MQTT update failed.")
else:
    st.info("No devices found.")

# --- Add New Device ---
with st.expander("➕ Register New Device"):

    with st.form("add_device_form"):
        new_device_name = st.text_input("Device Name")
        new_device_type = st.text_input("Device Type")
        submit = st.form_submit_button("Register Device")

        if submit:
            if not new_device_name.strip() or not new_device_type.strip():
                st.warning("Please fill in both fields.")
            else:
                payload = {
                    "name": new_device_name.strip(),
                    "device_type": new_device_type.strip(),
                }
                res = create_device(payload)
                if res.status_code == 201:
                    device = res.json()
                    st.success(f"✅ Device created! ID: {device['id']} | Key: {device['device_key']}")
                else:
                    st.error(f"❌ Failed to create device. ({res.status_code})")

