from pymongo import MongoClient
from config import Config

client = MongoClient(Config.MONGO_URI)

try:
    client.admin.command("ping")
    print("✅ MongoDB Atlas Authentication Successful")
except Exception as e:
    print("❌ MongoDB Atlas Connection Failed")
    print(e)

db = client["resumeai"]