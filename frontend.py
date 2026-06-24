"""
frontend.py
Simple Streamlit UI to test login, chat (rate-limited), and usage tracking.
"""

import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Day 20 - Rate Limiting Demo", page_icon="⏱️")
st.title("⏱️ Day 20 — Rate Limiting + Usage Tracking")

if "token" not in st.session_state:
    st.session_state.token = None

# --- LOGIN SECTION ---
if st.session_state.token is None:
    st.subheader("Login")
    username = st.text_input("Username", value="prashik")
    password = st.text_input("Password", type="password", value="mypassword123")

    if st.button("Login"):
        response = requests.post(
            f"{API_URL}/login",
            data={"username": username, "password": password}
        )
        if response.status_code == 200:
            st.session_state.token = response.json()["access_token"]
            st.success("Logged in!")
            st.rerun()
        else:
            st.error("Login failed. Check username/password.")

# --- MAIN APP (after login) ---
else:
    st.success("You are logged in.")
    headers = {"Authorization": f"Bearer {st.session_state.token}"}

    tab1, tab2 = st.tabs(["💬 Chat", "📊 Usage Stats"])

    with tab1:
        prompt = st.text_input("Ask something:")
        if st.button("Send"):
            response = requests.post(
                f"{API_URL}/chat",
                headers=headers,
                params={"prompt": prompt}
            )
            if response.status_code == 200:
                data = response.json()
                st.write("**Answer:**", data["answer"])
                st.caption(
                    f"Tokens used: {data['tokens_used']} | "
                    f"Cost: ${data['estimated_cost']} | "
                    f"Requests left this minute: {data['requests_remaining_this_minute']}"
                )
            elif response.status_code == 429:
                st.error(response.json()["detail"])
            else:
                st.error(f"Error: {response.text}")

    with tab2:
        if st.button("Refresh Stats"):
            response = requests.get(f"{API_URL}/usage", headers=headers)
            if response.status_code == 200:
                data = response.json()
                col1, col2, col3 = st.columns(3)
                col1.metric("Total Requests", data["total_requests"])
                col2.metric("Total Tokens", data["total_tokens_used"])
                col3.metric("Total Cost", f"${data['total_estimated_cost']}")
                st.dataframe(data["logs"])
            else:
                st.error("Could not fetch usage stats.")

    if st.button("Logout"):
        st.session_state.token = None
        st.rerun()