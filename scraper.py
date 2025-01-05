from selenium import webdriver
from selenium.webdriver.common.by import By
from pymongo import MongoClient
import uuid
from datetime import datetime
from selenium.webdriver.chrome.options import Options

# MongoDB setup
client = MongoClient('mongodb+srv://pratulmakar7:pratulmakar7@cluster0.7rikt.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')
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
    
    # Enter username and password
    username = driver.find_element(By.NAME, "text")
    username.send_keys("seleniumte12839")
    driver.find_element(By.XPATH, "//span[text()='Next']").click()
    
    # Wait for password field to load
    driver.implicitly_wait(5)
    password = driver.find_element(By.NAME, "password")
    password.send_keys("pratulMakar@@69")
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
