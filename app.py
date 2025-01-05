from flask import Flask, render_template, jsonify
import subprocess
from pymongo import MongoClient

app = Flask(__name__)

# MongoDB setup
client = MongoClient('mongodb+srv://pratulmakar7:pratulmakar7@cluster0.7rikt.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')
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
