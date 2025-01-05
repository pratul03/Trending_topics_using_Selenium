from flask import Blueprint, render_template, jsonify,request
from app.services.selenium_service import  login_and_fetch_X_trends
from app.services.mongodb_service import save_to_mongodb,get_all_records
import os

main = Blueprint('main', __name__)

@main.route('/')
def home():
    return render_template('index.html')

@main.route('/fetch_trends', methods=['GET'])
def fetch_trends():
    try:
        data = login_and_fetch_X_trends()
        print("Raw data:", data) 
        
        if not data or len(data) != 2:
            return render_template('index.html', trends=None, error="Failed to fetch data")
            
        ip_address, trends = data
        print(f"IP: {ip_address}, Trends: {trends}")  

        try:
            object_id = save_to_mongodb(trends, ip_address)
            print(f"MongoDB Object ID: {object_id}") 
        except Exception as e:
            return render_template('index.html', trends=trends, ip_address=ip_address, error=f"MongoDB Error: {str(e)}")

        return render_template('index.html', trends=trends, object_id=str(object_id), ip_address=ip_address)
    except Exception as e:
        print(f"Error: {str(e)}") 
        return render_template('index.html', trends=None, error=str(e))

@main.route('/dashboard', methods=['GET'])
def dashboard():
    try:
        records = get_all_records()
        return render_template('dashboard.html', records=records)
    except Exception as e:
        return render_template('dashboard.html', records=[], error=str(e))



