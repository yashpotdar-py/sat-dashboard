import time
from datetime import datetime

import folium
import requests
import streamlit as st
from streamlit_folium import folium_static

# Set page configuration and styling
try:
    st.set_page_config(
        page_title="Satellite Dashboard",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
except Exception as e:
    st.error(f"Error setting page config: {e}")

# API URL
API_URL = "http://54.146.171.112:5000/getSensorData"

# Function to fetch sensor data from the API


def fetch_sensor_data():
    try:
        response = requests.get(API_URL)
        print(f"Connecting to {API_URL}")
        if response.status_code == 200:
            print(f"Data fetched successfully: {response.json()}")
            return response.json()["data"]
        else:
            print(f"Error fetching data: {response.status_code}")
            st.error(f"Error fetching data: {response.status_code}")
            return []
    except requests.RequestException as e:
        st.error(f"Network Error: {e}")
        return []
    except ValueError as e:
        st.error(f"JSON Parsing Error: {e}")
        return []
    except Exception as e:
        st.error(f"Unexpected Error: {e}")
        return []

# Extract specific sensor data


def get_sensor_value(sensor_data, selector):
    try:
        for sensor in sensor_data:
            if sensor["selector"] == selector:
                print(f"Sensor {selector} data: {sensor['data']}")
                return sensor["data"]
        return "N/A"
    except Exception as e:
        print(f"Error getting sensor value: {e}")
        return "N/A"


# Dashboard title
try:
    st.title("Real-Time Satellite Dashboard")
    st.markdown('<p class="subheader">Live monitoring of environmental conditions</p>', unsafe_allow_html=True)
    last_update_placeholder = st.empty()
except Exception as e:
    st.error(f"Error rendering title: {e}")

# Create a placeholder for the sensor data
try:
    sensor_data_placeholder = st.empty()
    map_placeholder = st.empty()
except Exception as e:
    st.error(f"Error creating placeholder: {e}")
    sensor_data_placeholder = None
    map_placeholder = None

last_map_update = 0
while True:
    try:
        # Update last updated time
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        last_update_placeholder.markdown(f'<p style="font-size:10px">Last updated: {current_time}</p>', unsafe_allow_html=True)
        
        # Fetch sensor data
        sensor_data = fetch_sensor_data()

        with sensor_data_placeholder.container():
            # Display all sensor data on the same page
            st.markdown('<h2 class="subheader">Sensor Data Overview</h2>', unsafe_allow_html=True)

            try:
                col1, col2, col3, col4, col5 = st.columns(5)
            except Exception as e:
                st.error(f"Error creating columns: {e}")
                continue

            # Temperature
            try:
                with col1:
                    temperature = get_sensor_value(sensor_data, "1")
                    print("Temperature: ", temperature)
                    st.metric(
                        label="🌡️ Temperature",
                        value=f"{temperature} °C",
                        delta=None,
                        delta_color="normal"
                    )
            except Exception as e:
                st.error(f"Error displaying temperature: {e}")

            # Humidity
            try:
                with col2:
                    humidity = get_sensor_value(sensor_data, "2")
                    print("Humidity: ", humidity)
                    st.metric(
                        label="💧 Humidity",
                        value=f"{humidity} %",
                        delta=None,
                        delta_color="normal"
                    )
            except Exception as e:
                st.error(f"Error displaying humidity: {e}")

            # Altitude
            try:
                with col3:
                    altitude = get_sensor_value(sensor_data, "3")
                    print("Altitude: ", altitude)
                    st.metric(
                        label="🏔️ Altitude",
                        value=f"{altitude} m",
                        delta=None,
                        delta_color="normal"
                    )
            except Exception as e:
                st.error(f"Error displaying altitude: {e}")

            # Pressure
            try:
                with col4:
                    pressure = get_sensor_value(sensor_data, "4")
                    print("Pressure: ", pressure)
                    st.metric(
                        label="🌪️ Pressure",
                        value=f"{pressure} hPa",
                        delta=None,
                        delta_color="normal"
                    )
            except Exception as e:
                st.error(f"Error displaying pressure: {e}")

            # UV Index
            try:
                with col5:
                    uv_index = get_sensor_value(sensor_data, "5")
                    print("UV Index: ", uv_index)
                    st.metric(
                        label="☀️ UV Index",
                        value=uv_index,
                        delta=None,
                        delta_color="normal"
                    )
            except Exception as e:
                st.error(f"Error displaying UV index: {e}")
            st.markdown("---")

        # GPS Map
        current_time = time.time()
        if current_time - last_map_update >= 10:
            try:
                with map_placeholder.container():
                    st.markdown('<h2 class="subheader">GPS Location</h2>', unsafe_allow_html=True)
                    latitude = float(get_sensor_value(sensor_data, "6"))  # Assuming GPS latitude is sensor 6
                    longitude = float(get_sensor_value(sensor_data, "7"))  # Assuming GPS longitude is sensor 7
                    
                    col1, col2 = st.columns([1, 2])
                    
                    with col1:
                        st.metric(
                            label="📍 Latitude",
                            value=f"{latitude:.6f}°",
                            delta=None,
                            delta_color="normal"
                        )
                        st.metric(
                            label="📍 Longitude",
                            value=f"{longitude:.6f}°",
                            delta=None,
                            delta_color="normal"
                        )
                        st.markdown(f'<p style="font-size:10px">Map last updated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>', unsafe_allow_html=True)
                    
                    with col2:
                        m = folium.Map(location=[latitude, longitude], zoom_start=15)
                        # Add a marker for the current position
                        folium.Marker(
                            [latitude, longitude],
                            popup="Current Position",
                            icon=folium.Icon(color="red", icon="info-sign"),
                        ).add_to(m)
                        # Display the map
                        folium_static(m)
                last_map_update = current_time
            except Exception as e:
                st.error(f"Error displaying map: {e}")


    except Exception as e:
        st.error(f"Error in main loop: {e}")

    try:
        time.sleep(2)
    except KeyboardInterrupt:
        break
    except Exception as e:
        st.error(f"Error in sleep: {e}")
        time.sleep(5)  # Fallback sleep duration