from motor.motor_asyncio import AsyncIOMotorClient

# Database connection setup
mongo_url = "mongodb+srv://Epic2:w85NP8dEHmQxA5s7@cluster0.tttvsf9.mongodb.net/?retryWrites=true&w=majority"
client = AsyncIOMotorClient(mongo_url)
db = client['character_catcher']
sudo_users_collection = db['sudo_users_collection']