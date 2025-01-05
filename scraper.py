from selenium import webdriver
from selenium.webdriver.common.by import By
from pymongo import MongoClient
import uuid
from datetime import datetime
from selenium.webdriver.chrome.options import Options
from dotenv import load_dotenv
import os

# Load environment variables from .env
load_dotenv()

# MongoDB setup
MONGODB_URI = os.getenv('MONGODB_URI')
client = MongoClient(MONGODB_URI)
db = client['trendin_top5']
collection = db['trending_topics']

# Headless mode setup
options = Options()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

# Selenium setup with headless mode
driver = webdriver.Chrome(options=options)

try:
    # Navigate to Twitter and log in
    driver.get("https://twitter.com/login")
    
    # Fetch Twitter credentials from environment variables
    username_field = driver.find_element(By.NAME, "text")
    username_field.send_keys(os.getenv('TWITTER_USERNAME'))
    driver.find_element(By.XPATH, "//span[text()='Next']").click()
    
    # Wait for password field to load
    driver.implicitly_wait(5)
    password_field = driver.find_element(By.NAME, "password")
    password_field.send_keys(os.getenv('TWITTER_PASSWORD'))
    driver.find_element(By.XPATH, "//span[text()='Log in']").click()

    # Navigate to home page
    driver.implicitly_wait(10)
    driver.get("https://twitter.com/home")

    # Scrape trending topics
    trends = driver.find_elements(By.XPATH, "//section[contains(@aria-labelledby, 'accessible-list')]//span")
    trending_topics = [trend.text for trend in trends[:5]]

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

finally:
    driver.quit()
