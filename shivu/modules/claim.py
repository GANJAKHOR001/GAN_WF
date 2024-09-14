import asyncio
import html
from pyrogram import filters, Client, types as t
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from shivu import shivuu as bot
from shivu import user_collection, collection
from datetime import datetime, timedelta
from pyrogram.errors.exceptions.bad_request_400 import UserNotParticipant

DEVS = (6584789596)  # Developer user IDs
SUPPORT_CHAT_ID = -1002000314620  # Change this to your group's chat ID

keyboard = InlineKeyboardMarkup([
    [InlineKeyboardButton("Join Chat To Use Me", url="https://t.me/Grabbing_Your_WH_Group")],
    [InlineKeyboardButton("Join Chat To Use Me", url="https://t.me/Flex_Bots_News")]
])

# Functions
async def claim_toggle(claim_state):
    try:
        await collection.update_one({}, {"$set": {"claim": claim_state}}, upsert=True)
    except Exception as e:
        print(f"Error in claim_toggle: {e}")

async def get_claim_state():
    try:
        doc = await collection.find_one({})
        return doc.get("claim", "False")
    except Exception as e:
        print(f"Error in get_claim_state: {e}")
        return "False"

async def add_claim_user(user_id):
    try:
        await user_collection.update_one({"id": user_id}, {"$set": {"claim": True}}, upsert=True)
    except Exception as e:
        print(f"Error in add_claim_user: {e}")

async def del_all_claim_user():
    try:
        await user_collection.update_many({}, {"$unset": {"claim": ""}})
    except Exception as e:
        print(f"Error in del_all_claim_user: {e}")

async def get_claim_of_user(user_id):
    try:
        doc = await user_collection.find_one({"id": user_id})
        return doc.get("claim", False)
    except Exception as e:
        print(f"Error in get_claim_of_user: {e}")
        return False

async def get_unique_characters(receiver_id, target_rarities=['(🟢 Common', '🟣 Rare']):
    try:
        pipeline = [
            {'$match': {'rarity': {'$in': target_rarities}, 'id': {'$nin': [char['id'] for char in (await user_collection.find_one({'id': receiver_id}, {'characters': 1}))['characters']]}}},
            {'$sample': {'size': 1}}  # Adjust Num
        ]
        cursor = collection.aggregate(pipeline)
        characters = await cursor.to_list(length=None)
        return characters
    except Exception as e:
        print(f"Error in get_unique_characters: {e}")
        return []

# Dictionary to store last claim time for each user
last_claim_time = {}

@bot.on_message(filters.command(["startclaim"]) & filters.user(DEVS))
async def start_claim(_, message: t.Message):
    await claim_toggle("True")
    await message.reply_text("Claiming feature enabled!")

@bot.on_message(filters.command(["stopclaim"]) & filters.user(DEVS))
async def stop_claim(_, message: t.Message):
    await claim_toggle("False")
    await message.reply_text("Claiming feature disabled!")

@bot.on_message(filters.command(["claim"]))
async def claim(_, message: t.Message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    try:
        member = await bot.get_chat_member(-1002000314620, user_id)
        members = await bot.get_chat_member(-1002050050431, user_id)
        if not member or not members:
            await message.reply_text("You need to join the chat to use this feature.", reply_markup=keyboard)
            return 
        if chat_id != SUPPORT_CHAT_ID:
            return await message.reply_text("Command can only be used here: @Grabbing_Your_WH_Group")

        mention = message.from_user.mention

        # Check if the user is banned
        if user_id == 7162166061:
            return await message.reply_text(f"Sorry {mention}, you are banned from using this command.")

        # Check if the claiming feature is enabled
        claim_state = await get_claim_state()
        if claim_state == "False":
            return await message.reply_text("Claiming feature is currently disabled.")

        # Check if the user has already claimed a waifu today
        now = datetime.now()
        if user_id in last_claim_time:
            last_claim_date = last_claim_time[user_id]
            if last_claim_date.date() == now.date():
                next_claim_time = (last_claim_date + timedelta(days=1)).strftime("%H:%M:%S")
                return await message.reply_text(f"𝖸𝗈𝗎'𝗏𝖾 𝖺𝗅𝗋𝖾𝖺𝖽𝗒 𝖼𝗅𝖺𝗂𝗆𝖾𝖽 𝗒𝗈𝗎𝗋 𝖽𝖺𝗂𝗅𝗒 𝗋𝖾𝗂𝗇𝗌𝗅𝗋𝗎𝗉 𝗍𝗈𝖽𝖺𝗒.", quote=True)

        # Update the last claim time for the user
        last_claim_time[user_id] = now

        unique_characters = await get_unique_characters(user_id)
        if unique_characters:
            await user_collection.update_one({'id': user_id}, {'$push': {'characters': {'$each': unique_characters}}})
            img_urls = [character['img_url'] for character in unique_characters]
            captions = [
                f"<b>ᴄᴏɴɢʀᴀᴛᴜʟᴀᴛɪᴏɴ𝗌 🎊 {mention}!</b>\n\n\n<b>🎀 ɴᴀᴍᴇ :</b> {character['name']}\n\n<b>⚜️ ᴀɴɪᴍᴇ :</b> {character['anime']}\n\n\n<b>ᴄᴏᴍᴇ ᴀɢᴀɪɴ ᴛᴏᴍᴏʀʀᴏᴡ ғᴏʀ ʏᴏᴜʀ ɴᴇ𝗑ᴛ ᴄʟᴀɪᴍ 🍀</b>\n"
                for character in unique_characters
            ]
            for img_url, caption in zip(img_urls, captions):
                await message.reply_photo(photo=img_url, caption=caption, parse_mode='HTML')
        else:
            await message.reply_text("No characters found for claiming.")
    except Exception as e:
        print(f"An error occurred in claim: {e}")