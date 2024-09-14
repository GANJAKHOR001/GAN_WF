from pymongo import MongoClient
import os


MONGO_URI = os.getenv("mongodb+srv://mongo2:heyzxcyour61681843@cluster0.a6dvvjg.mongodb.net/?retryWrites=true&w=majority")
DB_NAME = os.getenv("DB_NAME", "Character_catcher")
COLLECTION_NAME = "anime_characters_lol"

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

def get_user_data(user_id):
    return collection.find_one({"user_id": user_id})

def save_user_data(user_id, user_data):
    collection.update_one({"user_id": user_id}, {"$set": user_data}, upsert=True)
    print("User data saved successfully.")