from motor.motor_asyncio import AsyncIOMotorClient

# Database connection setup
mongo_url = "mongodb+srv://mongodbflex:L3GxCeWU3UcgFZZX-hwjiwjve@cluster0.czbo8.mongodb.net/?retryWrites=true&w=majority"
client = AsyncIOMotorClient(mongo_url)
db = client['Character_catcher']
sudo_users_collection = db['sudo_users_collection']