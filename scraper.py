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
options.add_argument("--headless")  # Comment during debugging
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

# Selenium setup
driver = webdriver.Chrome(options=options)

try:
    # Navigate to Twitter login page
    driver.get("https://twitter.com/login")
    wait = WebDriverWait(driver, 20)

    # Log in to Twitter
    username_field = wait.until(EC.presence_of_element_located((By.NAME, "text")))
    username_field.send_keys(TWITTER_USERNAME)

    next_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[text()='Next']")))
    next_button.click()

    password_field = wait.until(EC.presence_of_element_located((By.NAME, "password")))
    password_field.send_keys(TWITTER_PASSWORD)

    login_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[text()='Log in']")))
    login_button.click()

    # Wait for home page to load
    wait.until(EC.presence_of_element_located((By.XPATH, "//section[contains(@aria-labelledby, 'accessible-list')]")))
    time.sleep(5)  # Ensure dynamic content has loaded

    # Scrape trending topics
    trends_elements = wait.until(EC.presence_of_all_elements_located(
        (By.XPATH, "//section[contains(@aria-labelledby, 'accessible-list')]//div[@data-testid='trend']//span")
    ))
    trending_topics = []
    for element in trends_elements:
        text = element.text.strip()
        if text and text not in trending_topics:
            trending_topics.append(text)

    # Limit to top 5 and handle gaps
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
