from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pymongo import MongoClient
from dotenv import load_dotenv
import uuid
from datetime import datetime
import os
from selenium.webdriver.chrome.options import Options
import time

# Load environment variables
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
TWITTER_USERNAME = os.getenv("TWITTER_USERNAME")
TWITTER_PASSWORD = os.getenv("TWITTER_PASSWORD")

# MongoDB setup
client = MongoClient(MONGO_URI)
db = client['trendin_top5']
collection = db['trending_topics']

# Headless mode setup
options = Options()
options.add_argument("--headless")  # Comment this line during debugging
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

# Selenium setup with headless mode
driver = webdriver.Chrome(options=options)

try:
    # Navigate to Twitter login page
    driver.get("https://twitter.com/login")
    wait = WebDriverWait(driver, 20)

    # Wait for username field and enter username
    username_field = wait.until(EC.presence_of_element_located((By.NAME, "text")))
    username_field.send_keys(TWITTER_USERNAME)

    # Click 'Next' button
    next_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[text()='Next']")))
    next_button.click()

    # Wait for password field and enter password
    password_field = wait.until(EC.presence_of_element_located((By.NAME, "password")))
    password_field.send_keys(TWITTER_PASSWORD)

    # Click 'Log in' button
    login_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[text()='Log in']")))
    login_button.click()

    # Wait for the home page to load
    wait.until(EC.presence_of_element_located((By.XPATH, "//section[contains(@aria-labelledby, 'accessible-list')]")))
    time.sleep(5)  # Ensure content has fully loaded

    # Scrape trending topics (use more specific and reliable XPath)
    trending_section = wait.until(EC.presence_of_all_elements_located(
        (By.XPATH, "//section[contains(@aria-labelledby, 'accessible-list')]//div[@dir='ltr']")
    ))
    trending_topics = [trend.text for trend in trending_section if trend.text.strip()]

    # Validate trends and handle gaps
    while len(trending_topics) < 5:
        trending_topics.append("N/A")

    # Use local IP address
    ip_address = "Local Machine"

    # Create unique ID and timestamp
    unique_id = str(uuid.uuid4())
    timestamp = datetime.now()

    # Store data in MongoDB
    record = {
        "_id": unique_id,
        "trend1": trending_topics[0],
        "trend2": trending_topics[1],
        "trend3": trending_topics[2],
        "trend4": trending_topics[3],
        "trend5": trending_topics[4],
        "timestamp": timestamp,
        "ip_address": ip_address
    }
    collection.insert_one(record)
    print("Record saved:", record)

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    driver.quit()
