import streamlit as st
import requests
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

# API URL (No API key needed)
API_URL = "https://jsonplaceholder.typicode.com/posts"

# Define the DataFetcher class
class DataFetcher:
    def __init__(self, api_url):
        self.api_url = api_url
    
    def fetch_data(self):
        """Fetch posts from the JSONPlaceholder API."""
        try:
            response = requests.get(self.api_url)
            response.raise_for_status()  # Check if the request was successful (status code 200)
            return response.json()  # Assuming the API returns JSON data
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching data from API: {e}")
            return None


# Define the Dashboard class
class Dashboard:
    def __init__(self, data_fetcher):
        self.data_fetcher = data_fetcher
    
    def display_posts(self):
        """Fetch posts data and display it on the Streamlit dashboard."""
        data = self.data_fetcher.fetch_data()
        
        if data:
            # Display first 5 posts for simplicity
            for post in data[:5]:
                st.subheader(post.get("title", "No Title"))
                st.write(post.get("body", "No Body"))
                st.write("---")
        else:
            st.error("Failed to retrieve posts data.")


# Streamlit UI
def main():
    st.title("Posts Dashboard")

    # Instantiate the DataFetcher and Dashboard objects
    data_fetcher = DataFetcher(API_URL)
    dashboard = Dashboard(data_fetcher)

    # Display the posts
    dashboard.display_posts()


if __name__ == "__main__":
    main()
