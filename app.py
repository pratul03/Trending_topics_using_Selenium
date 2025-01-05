from flask import Flask, render_template, jsonify
import subprocess
from pymongo import MongoClient
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

# MongoDB setup
client = MongoClient(MONGO_URI)
db = client['trendin_top5']
collection = db['trending_topics']

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/run-script', methods=['GET'])
def run_script():
    try:
        # Run the Selenium script
        subprocess.run(["python", "scraper.py"], check=True)
        
        # Fetch the latest record
        latest_record = collection.find().sort("timestamp", -1).limit(1)
        latest_record = list(latest_record)  # Convert to list for safe access

        if not latest_record:
            return jsonify({"error": "No records found"}), 404

        return jsonify(latest_record[0])
    except subprocess.CalledProcessError as e:
        return jsonify({"error": f"Script execution failed: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
