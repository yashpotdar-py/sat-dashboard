import logging
import time
from datetime import datetime

import pandas as pd
import requests
import streamlit as st

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Base classes
class BaseComponent:
    """Base class for all components."""

    def __init__(self, name):
        self.name = name

    def log(self, message):
        logging.debug(f"[{self.name}] {message}")


class BaseAPI:
    """Base class for API interactions."""
    API_URL = "http://54.146.171.112:5000/getSensorData"

    @staticmethod
    def fetch_data():
        try:
            logging.debug("Fetching data from API...")
            response = requests.get(BaseAPI.API_URL)
            if response.status_code == 200:
                logging.debug("Data fetched successfully.")
                return response.json()["data"]
            else:
                logging.error(f"API error: {response.status_code}")
                raise Exception(f"API error: {response.status_code}")
        except Exception as e:
            logging.error(f"Error fetching data: {e}")
            raise Exception(f"Error fetching data: {e}")


# Feature-specific classes
class SatSensors(BaseAPI):
    """Handles sensor data retrieval and processing."""
    @staticmethod
    def get_value(sensor_data, selector):
        try:
            logging.debug(f"Extracting value for selector: {selector}")
            for sensor in sensor_data:
                if sensor["selector"] == selector:
                    logging.debug(f"Value found: {sensor['data']}")
                    return sensor["data"]
            logging.debug("Value not found, returning 'N/A'.")
            return "N/A"
        except Exception as e:
            logging.error(f"Error extracting sensor value: {e}")
            raise Exception(f"Error extracting sensor value: {e}")


class MetricsComponent(BaseComponent):
    """Handles the display of sensor metrics."""

    def display_metrics(self, sensor_data):
        logging.debug("Displaying sensor metrics...")
        col1, col2, col3, col4, col5 = st.columns(5)

        metrics = [
            ("🌡️ Temperature", f"{SatSensors.get_value(sensor_data, '1')} °C"),
            ("💧 Humidity", f"{SatSensors.get_value(sensor_data, '2')} %"),
            ("🏔️ Altitude", f"{SatSensors.get_value(sensor_data, '3')} m"),
            ("🌪️ Pressure", f"{SatSensors.get_value(sensor_data, '4')} hPa"),
            ("☀️ UV Index", SatSensors.get_value(sensor_data, "5"))
        ]

        for idx, (label, value) in enumerate(metrics):
            with [col1, col2, col3, col4, col5][idx]:
                st.metric(label, value)
        logging.debug("Sensor metrics displayed.")


class MapComponent(BaseComponent):
    """Handles map display using Google Maps."""
    self.GOOGLE_MAPS_API_KEY = st.secrets['GOOGLE_MAPS_API_KEY']  # Replace with your API key

    def display_map(self, sensor_data):
        logging.debug("Displaying map...")
        latitude = float(SatSensors.get_value(sensor_data, "6"))
        longitude = float(SatSensors.get_value(sensor_data, "7"))
        # gpsData = SatSensors.get_value(sensor_data, "6")
        map_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <script src="https://maps.googleapis.com/maps/api/js?key={self.GOOGLE_MAPS_API_KEY}"></script>
            <style>
                #map {{
                    height: 500px;
                    width: 100%;
                    border-radius: 10px;
                }}
            </style>
        </head>
        <body>
            <div id="map"></div>
            <script>
                function initMap() {{
                    var location = {{ lat: {latitude}, lng: {longitude} }};
                    var map = new google.maps.Map(document.getElementById('map'), {{
                        zoom: 15,
                        center: location
                    }});
                    var marker = new google.maps.Marker({{
                        position: location,
                        map: map,
                        title: "Current Position"
                    }});
                }}
                window.onload = initMap;
            </script>
        </body>
        </html>
        """

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
            # st.write(gpsData)
        with col2:
            st.components.v1.html(map_html, height=500)
            # pass
        logging.debug("Map displayed.")


# Manager classes
class DashboardManager(BaseComponent):
    """Coordinates all dashboard components."""

    def __init__(self):
        super().__init__("DashboardManager")
        self.sensor_data = []

    def update_data(self):
        logging.debug("Updating sensor data...")
        self.sensor_data = SatSensors.fetch_data()

    def render(self):
        logging.debug("Rendering dashboard...")
        st.markdown("<h1 style='text-align: center;'>Real-Time Satellite Dashboard</h1>", unsafe_allow_html=True)
        st.markdown('<p class="subheader" style="text-align: center;">Live monitoring of environmental conditions</p>', unsafe_allow_html=True)
        st.markdown(f'<p style="font-size:14px">Map last updated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>', unsafe_allow_html=True)
        st.markdown("---")

        metrics_placeholder = st.empty()
        metrics_placeholder.markdown("### Sensor Metrics")
        metrics = MetricsComponent("Metrics")
        metrics.display_metrics(self.sensor_data)

        st.markdown("---")

        map_component_placeholder = st.empty()
        map_component_placeholder.markdown("### GPS Map")
        map_component = MapComponent("Map")
        map_component.display_map(self.sensor_data)

        st.markdown("---")
        logging.debug("Dashboard rendered.")


class AppManager(BaseComponent):
    """Manages the entire application."""

    def __init__(self):
        super().__init__("AppManager")
        self.dashboard_manager = DashboardManager()

    def run(self):
        st.sidebar.title("Navigation")
        page = st.sidebar.radio("Go to", ["Dashboard", "Data Export"])

        if page == "Dashboard":
            logging.debug("Rendering Dashboard page...")
            self.dashboard_manager.update_data()
            self.dashboard_manager.render()

            # Only update the data every 2 seconds (update only specific components)
            time.sleep(2)
            st.rerun()

            if "last_update" not in st.session_state:
                st.session_state.last_update = time.time()

            elif time.time() - st.session_state.last_update >= 2:
                st.session_state.last_update = time.time()
                self.dashboard_manager.update_data()  # Fetch fresh data
                self.dashboard_manager.render()

        elif page == "Data Export":
            self.data_export_page()

    def data_export_page(self):
        logging.debug("Rendering Data Export page...")
        st.title("Data Export")
        st.write("Export collected data to CSV or Excel.")

        # Example dummy data
        data = [{"sensor": "Temperature", "value": 25},
                {"sensor": "Humidity", "value": 60}]

        df = pd.DataFrame(data)

        st.dataframe(df)
        csv = df.to_csv(index=False)
        st.download_button("Download CSV", csv, "data.csv", "text/csv")
        logging.debug("Data Export page rendered.")


# Main execution
if __name__ == "__main__":
    try:
        st.set_page_config(
            page_title="Satellite Dashboard",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        logging.info("Streamlit page configuration set.")
    except Exception as e:
        st.error(f"Error setting page config: {e}")
        logging.error(f"Error setting page config: {e}")

    st.markdown(
        """
        <style>
        .css-18e3th9 {
            padding-top: 2rem;
        }
        .subheader {
            font-size: 1.2rem;
            color: #6c757d;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    app = AppManager()
    app.run()
