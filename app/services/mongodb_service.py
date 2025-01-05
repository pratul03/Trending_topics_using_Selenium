from pymongo import MongoClient
from datetime import datetime
from app.config import Config

MONGODB_URI = Config.MONGODB_URI
DB_NAME = Config.DB_NAME
COLLECTION_NAME = Config.COLLECTION_NAME

client = MongoClient(MONGODB_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

def get_all_records():
    try:
        global client, db, collection
        # Check if client is closed and reconnect if necessary
        if not client.is_primary:  
            client = MongoClient(MONGODB_URI)
            db = client[DB_NAME]
            collection = db[COLLECTION_NAME]
        
        records = list(collection.find())
        
        # Convert ObjectId to string 
        for record in records:
            record['_id'] = str(record['_id'])
        
        return records
    except Exception as e:
        print(f"Error retrieving records from MongoDB: {e}")
        return []

def save_to_mongodb(trends, ip_address):
    try:
        global client, db, collection

        if not client.is_primary:
            client = MongoClient(MONGODB_URI)
            db = client[DB_NAME]
            collection = db[COLLECTION_NAME]

        document = {
            "trends": trends,
            "timestamp": datetime.now(),
            "ip_address": ip_address
        }
        result = collection.insert_one(document)
        return result.inserted_id
    except Exception as e:
        print(f"Error saving to MongoDB: {e}")
        return None
