from motor.motor_asyncio import AsyncIOMotorClient

# Database connection setup
mongo_url = "mongodb+srv://mongo2:heyzxcyour61681843@cluster0.a6dvvjg.mongodb.net/?retryWrites=true&w=majority"
client = AsyncIOMotorClient(mongo_url)
db = client['Character_catcher']
sudo_users_collection = db['sudo_users_collection']