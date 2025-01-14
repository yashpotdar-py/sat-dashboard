import time
from datetime import datetime

import requests
import streamlit as st

# Set page configuration and styling
st.set_page_config(
    page_title="Satellite Dashboard",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# API URL
API_URL = "http://54.146.171.112:5000/getSensorData"

# Function to fetch sensor data from the API


def fetch_sensor_data():
    try:
        response = requests.get(API_URL)
        if response.status_code == 200:
            return response.json()["data"]
        else:
            st.error(f"Error fetching data: {response.status_code}")
            return []
    except Exception as e:
        st.error(f"Error: {e}")
        return []

# Extract specific sensor data


def get_sensor_value(sensor_data, selector):
    for sensor in sensor_data:
        if sensor["selector"] == selector:
            return sensor["data"]
    return "N/A"



# Dashboard title
st.title("Real-Time Satellite Dashboard")
st.markdown('<p class="subheader">Live monitoring of environmental conditions</p>', unsafe_allow_html=True)

# Create a placeholder for the sensor data
sensor_data_placeholder = st.empty()

while True:
    # Fetch sensor data
    sensor_data = fetch_sensor_data()

    with sensor_data_placeholder.container():
        # Display all sensor data on the same page

        st.markdown('<h2 class="subheader">Sensor Data Overview</h2>', unsafe_allow_html=True)

        col1, col2, col3, col4, col5 = st.columns(5)

        # Temperature
        with col1:
            temperature = get_sensor_value(sensor_data, "1")

            st.metric(
                label="🌡️ Temperature",
                value=f"{temperature} °C",
                delta=None,
                delta_color="normal"
            )

        # Humidity
        with col2:
            humidity = get_sensor_value(sensor_data, "2")

            st.metric(
                label="💧 Humidity",
                value=f"{humidity} %",
                delta=None,
                delta_color="normal"
            )

        # Altitude
        with col3:
            altitude = get_sensor_value(sensor_data, "3")

            st.metric(
                label="🏔️ Altitude",
                value=f"{altitude} m",
                delta=None,
                delta_color="normal"
            )

        # Pressure
        with col4:
            pressure = get_sensor_value(sensor_data, "4")

            st.metric(
                label="🌪️ Pressure",
                value=f"{pressure} hPa",
                delta=None,
                delta_color="normal"
            )

        # UV Index
        with col5:
            uv_index = get_sensor_value(sensor_data, "5")

            st.metric(
                label="☀️ UV Index",
                value=uv_index,
                delta=None,
                delta_color="normal"
            )

        # Footer
        st.markdown("---")

        st.markdown(
            '<div class="footer">Real-time sensor dashboard built with ❤️<br>'
            f'Last updated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</div>',
            unsafe_allow_html=True
        )

    time.sleep(2)
