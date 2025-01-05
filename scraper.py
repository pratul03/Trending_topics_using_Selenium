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
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

# Selenium setup with headless mode
driver = webdriver.Chrome(options=options)

try:
    # Navigate to Twitter login page
    driver.get("https://twitter.com/login")
    
    # Wait for username field and enter username
    wait = WebDriverWait(driver, 10)
    username_field = wait.until(EC.presence_of_element_located((By.NAME, "session[username_or_email]")))
    username_field.send_keys(TWITTER_USERNAME)

    # Click 'Next' button
    next_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[text()='Next']")))
    next_button.click()

    # Wait for password field and enter password
    password_field = wait.until(EC.presence_of_element_located((By.NAME, "password")))
    password_field.send_keys(TWITTER_PASSWORD)
    login_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[text()='Log in']")))
    login_button.click()

    # Navigate to home page and scrape trending topics
    wait.until(EC.presence_of_element_located((By.XPATH, "//section[contains(@aria-labelledby, 'accessible-list')]")))
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
        "trend1": trending_topics[0] if len(trending_topics) > 0 else "N/A",
        "trend2": trending_topics[1] if len(trending_topics) > 1 else "N/A",
        "trend3": trending_topics[2] if len(trending_topics) > 2 else "N/A",
        "trend4": trending_topics[3] if len(trending_topics) > 3 else "N/A",
        "trend5": trending_topics[4] if len(trending_topics) > 4 else "N/A",
        "timestamp": timestamp,
        "ip_address": ip_address
    }
    collection.insert_one(record)

finally:
    driver.quit()
