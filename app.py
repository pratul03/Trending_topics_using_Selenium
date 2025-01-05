from flask import Flask, render_template, jsonify
import subprocess
from pymongo import MongoClient
from dotenv import load_dotenv
import os

# Load environment variables from .env
load_dotenv()

# Flask app setup
app = Flask(__name__)

# MongoDB setup
MONGODB_URI = os.getenv('MONGODB_URI')
client = MongoClient(MONGODB_URI)
db = client['trendin_top5']
collection = db['trending_topics']

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/run-script')
def run_script():
    # Run the Selenium script
    subprocess.run(["python", "scraper.py"])
    
    # Fetch the latest record
    latest_record = collection.find().sort("timestamp", -1).limit(1)[0]
    return jsonify(latest_record)

if __name__ == '__main__':
    app.run(debug=True)
