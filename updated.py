from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import pandas as pd
from datetime import datetime
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.edge.options import Options as EdgeOptions
import os
import json
import firebase_admin
from firebase_admin import credentials, firestore
import re
# Initialize Firebase
def initialize_firebase(api_key_json_path):
    cred = credentials.Certificate(api_key_json_path)
    firebase_admin.initialize_app(cred)
    return firestore.client()

# Function to scrape followers count from a LinkedIn profile
def login_and_scrape(profile_link, browser_type):
    # Set up the driver based on the browser type
    driver = None
    if browser_type == "firefox":
        firefox_options = FirefoxOptions()
        firefox_options.headless = False
        firefox_service = FirefoxService()
        driver = webdriver.Firefox(service=firefox_service, options=firefox_options)
    elif browser_type == "edge":
        edge_options = EdgeOptions()
        edge_options.headless = False
        edge_service = EdgeService()
        driver = webdriver.Edge(service=edge_service, options=edge_options)

    # Open the LinkedIn page for the specified profile link
    driver.get(profile_link)
    time.sleep(2)

    # Click the cross button to dismiss the login prompt
    try:
        crossbutton = driver.find_element(by=By.XPATH, value='//*[@id="base-contextual-sign-in-modal"]/div/section/button')
        crossbutton.click()
        time.sleep(2)
    except Exception as e:
        print(f"No login pop-up found or unable to close it: {e}")

    # Now, let's scrape the followers count
    try:
    # Locate the element containing the followers count using an appropriate XPath or CSS selector
        followers_element = driver.find_element(by=By.CSS_SELECTOR, value='#main-content > section.core-rail.mx-auto.papabear\:w-core-rail-width.mamabear\:max-w-\[790px\].babybear\:max-w-\[790px\] > section > div > div.top-card-layout__entity-info-container.flex.flex-wrap.papabear\:flex-nowrap > div:nth-child(1) > h3')
        followers_text = followers_element.text
    # Extract only the numeric value from the followers count using regex
        followers_count = re.sub(r'\D', '', followers_text)
        print(f"Followers count: {followers_count}")
    except Exception as e:
        print(f"Unable to find followers count: {e}")
        driver.quit()  # Ensure the driver quits on error
        return  # Exit if unable to scrape followers

    # Extract name from the profile link (assuming the name is known or can be passed)
    name = profile_link.split('/')[-2]

    # Prepare data for Firebase
    current_time = datetime.now()
    date = current_time.strftime("%Y-%m-%d")
    day = current_time.strftime("%A")
    time_str = current_time.strftime("%H:%M:%S")

    data = {
        "Name": name,
        "Followers Count": followers_count,
        "Date": date,
        "Day": day,
        "Time": time_str
    }

    # Store data in Firebase
    firestore_client = initialize_firebase('C:/Users/Pon Karthik/OneDrive/Desktop/sma/trialgitcobol-firebase-adminsdk-7azo0-6f75e8626e.json')  # Replace with your JSON path
    firestore_client.collection('followers_data').add(data)
    print(f"Data saved to Firebase: {data}")

    time.sleep(15)
    driver.quit()  # Quit the driver after scraping the profile

# Load profile links from CSV
def load_profiles(csv_file_path):
    df = pd.read_csv(csv_file_path)
    return df[['Name', 'profile_link']].values.tolist()

# Main loop to scrape data
def main():
    profiles = load_profiles('input_profiles.csv')
    browser_types = ["firefox", "edge"]  # List of browsers to use
    round_num = 0  # Track the number of rounds

    while True:  # Infinite loop to repeat the scraping process
        for idx, profile in enumerate(profiles):
            name, profile_link = profile
            browser_type = browser_types[(idx + round_num) % 2]  # Alternate browsers
            print(f"Using {browser_type} for profile: {profile_link}")
            login_and_scrape(profile_link, browser_type)

        round_num += 1  # Increment round number after each round of scraping
        print("Completed one round of scraping. Waiting for 10 minutes before the next round...")
        time.sleep(600)  # Wait for 10 minutes

if __name__ == "__main__":
    main()
