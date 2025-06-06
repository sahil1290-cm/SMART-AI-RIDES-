import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

# --- Config ---
st.set_page_config(page_title="RiDeal App", layout="centered")

# Dummy User Auth
users = {"admin": "1234"}
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False
if 'points' not in st.session_state:
    st.session_state['points'] = 40

# --- Modern Mobile UI CSS ---
st.markdown("""
<style>
    html, body, [class*="css"] {
        font-family: 'Segoe UI', sans-serif;
        background-color: #f5f7fa;
    }
    .main {
        max-width: 400px;
        margin: auto;
    }
    h1, h2, h3 {
        color: #333333;
        text-align: center;
    }
    .stButton>button {
        width: 100%;
        border-radius: 12px;
        background-color: #ff6600 !important;
        color: white !important;
        height: 3em;
        font-weight: bold;
        border: none;
    }
    .stTextInput>div>div>input {
        border-radius: 12px;
        padding: 0.6em;
    }
    .card {
        background: white;
        padding: 1em;
        margin-bottom: 1em;
        border-radius: 16px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.07);
    }
    ul {
        padding-left: 1.2em;
    }
    .nav-radio label {
        font-weight: bold;
        padding: 0.5em;
        border-radius: 10px;
        background: #ff6600;
        color: white;
        margin-right: 5px;
    }
</style>
""", unsafe_allow_html=True)

# --- Login Page ---
def login_ui():
    st.image("C:\\Users\\ACER\\Downloads\\ai recommendation app\\image\\retro-car-logo-on-transparent-banckground-png.webp", width=64)
    st.title("🚖 RiDeal")
    tab1, tab2 = st.tabs(["🔐 Login", "🆕 Sign Up"])

    with tab1:
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            if username in users and users[username] == password:
                st.session_state['authenticated'] = True
                st.success("Welcome back!")
            else:
                st.error("Invalid credentials.")

    with tab2:
        new_user = st.text_input("New Username")
        new_pass = st.text_input("New Password", type="password")
        if st.button("Create Account"):
            if new_user in users:
                st.warning("User already exists.")
            else:
                users[new_user] = new_pass
                st.success("Account created!")

# --- Main App ---
def ride_app():
    st.title("🧠 Smart AI Ride Planner")

    page = st.radio("Navigate", ["🔌 Sync Apps", "📍 Search", "🎛️ Filter + Book", "🎯 My Points"], horizontal=True, key="nav")

    csv_path = "C:\\Users\\ACER\\Downloads\\ai recommendation app\\smart_ai_ride_data.csv"
    try:
        ride_data = pd.read_csv(csv_path)
        ride_data.columns = ride_data.columns.str.strip()
    except:
        st.error("❌ Ride data CSV not found.")
        return

    coords = {
        "Chicago": [41.8781, -87.6298],
        "Houston": [29.7604, -95.3698],
        "Los Angeles": [34.0522, -118.2437],
        "New York": [40.7128, -74.0060],
        "San Francisco": [37.7749, -122.4194],
        "Phoenix": [33.4484, -112.0740],
        "Seattle": [47.6062, -122.3321],
    }

    if page == "🔌 Sync Apps":
        st.header("🔗 Sync Ride Apps")
        st.image("https://img.icons8.com/color/48/synchronize.png", width=40)
        st.write("Choose which apps to sync:")
        apps = ['Uber', 'Lyft', 'Bird', 'Curb', 'FlixBus']
        for app in apps:
            st.toggle(f"✅ {app}")
        st.success("Apps synced successfully!")

    elif page == "📍 Search":
        st.header("🗺️ Choose Your Route")
        col1, col2 = st.columns(2)
        with col1:
            origin = st.selectbox("From", sorted(ride_data['Origin'].dropna().unique()))
        with col2:
            destination = st.selectbox("To", sorted(ride_data['Destination'].dropna().unique()))

        if origin == destination:
            st.warning("⚠️ Origin and destination must differ.")
        else:
            st.session_state['origin'] = origin
            st.session_state['destination'] = destination

            map_ = folium.Map(location=coords.get(origin, [37.773972, -122.431297]), zoom_start=5)
            folium.Marker(location=coords.get(origin, [0, 0]), tooltip=f"From: {origin}").add_to(map_)
            folium.Marker(location=coords.get(destination, [0, 0]), tooltip=f"To: {destination}").add_to(map_)
            st_folium(map_, width=390)
            st.success("✅ Route saved! Now head to '🎛️ Filter + Book'.")

    elif page == "🎛️ Filter + Book":
        st.header("🔍 Refine Your Ride Options")

        if 'origin' not in st.session_state or 'destination' not in st.session_state:
            st.warning("🔎 Please search for a route first.")
            return

        origin = st.session_state['origin']
        destination = st.session_state['destination']
        st.markdown(f"**📍 Route:** {origin} → {destination}")

        filtered = ride_data[
            (ride_data['Origin'] == origin) & 
            (ride_data['Destination'] == destination)
        ]

        col1, col2 = st.columns(2)
        with col1:
            selected_mode = st.selectbox("Vehicle Type", ['All'] + sorted(ride_data['Mode'].dropna().unique()))
        with col2:
            sort_order = st.selectbox("Sort By", ['Price: Low to High', 'Price: High to Low'])

        price_min = float(ride_data['Price'].min())
        price_max = float(ride_data['Price'].max())
        price_range = st.slider("💸 Price Range ($)", price_min, price_max, (20.0, 80.0))

        if selected_mode != "All":
            filtered = filtered[filtered['Mode'] == selected_mode]
        filtered = filtered[(filtered['Price'] >= price_range[0]) & (filtered['Price'] <= price_range[1])]
        filtered = filtered.sort_values("Price", ascending=sort_order == 'Price: Low to High')

        st.subheader("🚗 Available Rides")
        if filtered.empty:
            st.warning("😕 No matching rides found.")
        else:
            for i, ride in filtered.iterrows():
                with st.container():
                    st.markdown(f"""
                    <div class='card'>
                        <h4>{ride['App']} — {ride['Mode']}</h4>
                        <p>🧭 {ride['Origin']} → {ride['Destination']}</p>
                        <p>🕒 {ride['DepartureHour']}:00 → {ride['ArrivalHour']}:00</p>
                        <p>💰 <strong>${ride['Price']}</strong></p>
                    </div>
                    """, unsafe_allow_html=True)
                    if st.button(f"🚕 Book with {ride['App']}", key=f"{i}-{ride['App']}"):
                        st.success(f"🎉 Ride booked with {ride['App']}! ETA: {ride['ArrivalHour']}:00.")
                        st.session_state['points'] += 10

    elif page == "🎯 My Points":
        st.header("🏆 Your Reward Points")
        points = st.session_state['points']
        st.markdown(f"""
        <div class='card'>
            <h2 style='text-align:center;'>💎 {points} Points</h2>
            <p>Level: <strong>{points // 40 + 1}</strong></p>
            <ul>
                <li>🎉 2x bonus points per booking</li>
                <li>🎁 Free Bird ride day</li>
                <li>🚕 Home ride voucher</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

# --- App Launcher ---
if not st.session_state['authenticated']:
    login_ui()
else:
    ride_app()
