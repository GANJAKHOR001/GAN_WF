import re
import time
from html import escape
from cachetools import TTLCache
from pymongo import MongoClient, ASCENDING
from telegram import Update, InlineQueryResultPhoto, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import InlineQueryHandler, CallbackQueryHandler, CallbackContext
from shivu import user_collection, collection, application, db


# Setting up indexes for collections
db.characters.create_index([('id', ASCENDING)])
db.characters.create_index([('anime', ASCENDING)])
db.characters.create_index([('img_url', ASCENDING)])

db.user_collection.create_index([('characters.id', ASCENDING)])
db.user_collection.create_index([('characters.name', ASCENDING)])
db.user_collection.create_index([('characters.img_url', ASCENDING)])

# Caching
all_characters_cache = TTLCache(maxsize=10000, ttl=36000)
user_collection_cache = TTLCache(maxsize=10000, ttl=60)

async def inlinequery(update: Update, context: CallbackContext) -> None:
    query = update.inline_query.query
    offset = int(update.inline_query.offset) if update.inline_query.offset else 0

    # Handling user collections
    if query.startswith('collection.'):
        user_id, *search_terms = query.split(' ')[0].split('.')[1], ' '.join(query.split(' ')[1:])
        if user_id.isdigit():
            user = user_collection_cache.get(user_id) or await user_collection.find_one({'id': int(user_id)})
            user_collection_cache[user_id] = user

            if user:
                all_characters = list({v['id']: v for v in user['characters']}.values())
                if search_terms:
                    regex = re.compile(' '.join(search_terms), re.IGNORECASE)
                    all_characters = [character for character in all_characters if regex.search(character['name']) or regex.search(character['rarity']) or regex.search(character['id']) or regex.search(character['anime'])]
            else:
                all_characters = []
        else:
            all_characters = []
    else:
        # Handling global queries
        if query:
            regex = re.compile(query, re.IGNORECASE)
            all_characters = list(await collection.find({
                "$or": [
                    {"name": regex},
                    {"rarity": regex},
                    {"id": regex},
                    {"anime": regex}
                ]
            }).to_list(length=None))
        else:
            all_characters = all_characters_cache.get('all_characters') or list(await collection.find({}).to_list(length=None))
            all_characters_cache['all_characters'] = all_characters

    # Handling pagination and results
    characters = all_characters[offset:offset + 50]
    next_offset = str(offset + 50 if len(characters) > 50 else offset + len(characters))

    results = []
    for character in characters:
        global_count = await user_collection.count_documents({'characters.id': character['id']})
        anime_characters = await collection.count_documents({'anime': character['anime']})

        if query.startswith('collection.'):
            user_character_count = sum(c['id'] == character['id'] for c in user['characters'])
            user_anime_characters = sum(c['anime'] == character['anime'] for c in user['characters'])
            caption = (
                f"<b> Lᴏᴏᴋ Aᴛ <a href='tg://user?id={user['id']}'>{escape(user.get('first_name', user['id']))}</a>'s Hᴜsʙᴀɴᴅᴏ....!!</b>\n\n"
                f"<b>{character['id']}:</b> {character['name']} x{user_character_count}\n"
                f"<b>{character['anime']}</b> {user_anime_characters}/{anime_characters}\n"
                f"﹙<b>{character['rarity'][0]} 𝙍𝘼𝙍𝙄𝙏𝙔:</b> {character['rarity'][2:]}﹚\n"
            )
        else:
            caption = (
                f"<b>Lᴏᴏᴋ Aᴛ Tʜɪs Hᴜsʙᴀɴᴅᴏ....!!</b>\n\n"
                f"<b>{character['id']}:</b> {character['name']}\n"
                f"<b>{character['anime']}</b>\n"
                f"﹙<b>{character['rarity'][0]} 𝙍𝘼𝙍𝙄𝙏𝙔:</b> {character['rarity'][2:]}﹚\n"
                f"<b>Gʟᴏʙᴀʟʟʏ Gʀᴀʙ {global_count} Times...</b>"
            )

        # Button for showing top grabbers
        button = InlineKeyboardMarkup([[InlineKeyboardButton("Top Grabbers", callback_data=f"show_grabbers_{character['id']}")]])

        results.append(
            InlineQueryResultPhoto(
                thumbnail_url=character['img_url'],
                id=f"{character['id']}_{time.time()}",
                photo_url=character['img_url'],
                caption=caption,
                parse_mode='HTML',
                reply_markup=button
            )
        )

    await update.inline_query.answer(results, next_offset=next_offset, cache_time=5)

async def show_grabbers_callback(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    character_id = query.data.split('_')[2]

    # Fetch top 10 users who grabbed this character
    top_users = await user_collection.aggregate([
        {'$match': {'characters.id': character_id}},
        {'$unwind': '$characters'},
        {'$match': {'characters.id': character_id}},
        {'$group': {'_id': '$id', 'count': {'$sum': 1}}},
        {'$sort': {'count': -1}},
        {'$limit': 10}
    ]).to_list(length=10)

    # Build grabbers text
    grabbers_text = "<b>ᴛᴏᴘ 𝟷𝟶 ᴜsᴇʀs ᴡʜᴏ ɢʀᴀʙʙᴇʀs ᴛɪᴍᴇ ɪɴ ᴛʜɪs ɢʀᴏᴜᴘ....</b>\n\n"
    for i, user in enumerate(top_users, start=1):
        username = user.get('username', 'Unknown')
        first_name = escape(user.get('first_name', 'Unknown'))

        if len(first_name) > 15:
            first_name = first_name[:15] + '...'
        
        grabbers_text += f'{i}. <a href="https://t.me/{username}"><b>{first_name}</b></a> ➾ <b>{user["count"]}</b>\n'

    # Editing the message (text or caption)
    if query.message.text:
        await query.edit_message_caption(caption=query.message.caption + grabbers_text, parse_mode='HTML')
    else:
        await query.edit_message_text(text=query.message.text + grabbers_text, parse_mode='HTML')

# Adding handlers to the application
application.add_handler(CallbackQueryHandler(show_grabbers_callback, pattern=r'^show_grabbers_'))
application.add_handler(InlineQueryHandler(inlinequery, block=False))