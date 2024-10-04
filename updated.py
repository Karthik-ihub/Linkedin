from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import pandas as pd
from datetime import datetime
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from webdriver_manager.firefox import GeckoDriverManager
import firebase_admin
from firebase_admin import credentials, firestore
import re

# Initialize Firebase
def initialize_firebase(api_key_json_path):
    cred = credentials.Certificate(api_key_json_path)
    firebase_admin.initialize_app(cred)
    return firestore.client()

# Function to scrape followers count from a LinkedIn profile
def login_and_scrape(profile_link):
    # Set up Firefox with WebDriverManager on Windows
    firefox_options = FirefoxOptions()
    firefox_options.headless = False  # Set to True if you want to run headless (without opening a window)

    # Explicitly set the Firefox binary location (adjust the path to your system's location)
    firefox_options.binary_location = r"C:\Program Files\Mozilla Firefox\firefox.exe"

    # Use the Service class to manage the geckodriver
    firefox_service = FirefoxService(GeckoDriverManager().install())
    
    driver = webdriver.Firefox(service=firefox_service, options=firefox_options)

    # Open the LinkedIn page for the specified profile link
    driver.get(profile_link)
    time.sleep(2)

    # Try to close login pop-up
    try:
        crossbutton = driver.find_element(by=By.XPATH, value='//*[@id="base-contextual-sign-in-modal"]/div/section/button')
        crossbutton.click()
        time.sleep(2)
    except Exception as e:
        print(f"No login pop-up found or unable to close it: {e}")

    # Scrape the followers count
    try:
        followers_element = driver.find_element(by=By.CSS_SELECTOR, value='#main-content > section ...')
        followers_text = followers_element.text
        followers_count = re.sub(r'\D', '', followers_text)
        print(f"Followers count: {followers_count}")
    except Exception as e:
        print(f"Unable to find followers count: {e}")
        driver.quit()
        return

    # Close the driver after scraping
    driver.quit()

# Main function to call scraping
if __name__ == "__main__":
    profile_link = 'https://www.linkedin.com/in/sample-profile'
    login_and_scrape(profile_link)
