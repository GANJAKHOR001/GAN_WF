class Config(object):
    LOGGER = True

    # Get this value from my.telegram.org/apps
    OWNER_ID = "6903379369"
    sudo_users = ["6903379369"]
    GROUP_ID = "-1002460622908"
    TOKEN = "7463997374:AAGSyJyWVN0HiVCerV_OS_tfgvW49MixOKQ"
    mongo_url = "mongodb+srv://surajislam589:surajislam589@cluster0.2fjjb1e.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
    PHOTO_URL = ["https://telegra.ph//file/e64337bbc6cdac7e6b178.jpg", "https://telegra.ph/file/ed23556d07d33db18402d.jpg", "https://telegra.ph//file/32556c77847dff110577c.jpg", "https://telegra.ph//file/0650844fc5db4049959bc.jpg"]
    SUPPORT_CHAT = "+aB3TQoPJ2dBjZGU1"
    UPDATE_CHAT = "+aB3TQoPJ2dBjZGU1"
    BOT_USERNAME = "misskittymusicbot"
    CHARA_CHANNEL_ID = "-1002457181322"
    api_id = "20533795"
    api_hash = "f6cadf28523943f525e706e6ace8a250"

    
class Production(Config):
    LOGGER = True


class Development(Config):
    LOGGER = True
