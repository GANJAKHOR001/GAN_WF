#FLEXdub_Official
import re
import time
import html
import logging
from telegram import Update
from telegram.ext import CallbackContext, CallbackQueryHandler
from html import escape
from cachetools import TTLCache
from pymongo import ASCENDING
from telegram import Update, InlineQueryResultPhoto, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import InlineQueryHandler, CallbackQueryHandler, CallbackContext
from shivu import user_collection, collection, application, db

# Setup MongoDB indexes
def setup_indexes():
    db.characters.create_index([('id', ASCENDING)])
    db.characters.create_index([('anime', ASCENDING)])
    db.characters.create_index([('img_url', ASCENDING)])
    db.user_collection.create_index([('characters.id', ASCENDING)])
    db.user_collection.create_index([('characters.name', ASCENDING)])
    db.user_collection.create_index([('characters.img_url', ASCENDING)])

setup_indexes()

# Setup caching
all_characters_cache = TTLCache(maxsize=10000, ttl=36000)
user_collection_cache = TTLCache(maxsize=10000, ttl=60)

# Tag mappings
tag_mappings = {
    '👘': '👘𝑲𝒊𝒎𝒐𝒏𝒐👘',
    '☃️': '☃️𝑾𝒊𝒏𝒕𝒆𝒓☃️',
    '🐰': '🐰𝑩𝒖𝒏𝒏𝒚🐰',
    '🎮': '🎮𝑮𝒂𝒎𝒆🎮',
    '🎄': '🎄𝑪𝒓𝒊𝒔𝒕𝒎𝒂𝒔🎄',
    '🎃': '🎃𝑯𝒆𝒍𝒍𝒐𝒘𝒆𝒆𝒏🎃',
    '🏖️': '🏖️𝑺𝒖𝒎𝒎𝒆𝒓🏖️',
    '🧹': '🧹𝑴𝒂𝒅𝒆🧹',
    '🥻': '🥻𝑺𝒂𝒓𝒆𝒆🥻',
    '☔': '☔𝑴𝒐𝒏𝒔𝒐𝒐𝒏☔',
    '🎒': '🎒𝑺𝒄𝒉𝒐𝒐𝒍🎒',
    '🎩': '🎩𝑻𝒖𝒙𝒆𝒅𝒐🎩',
    '👥': '👥𝐃𝐮𝐨👥',
    '🤝🏻': '🤝🏻𝐆𝐫𝐨𝐮𝐩🤝🏻',
    '👑': '👑𝑳𝒐𝒓𝒅👑',
    '💍': '💍𝑾𝒆𝒅𝒅𝒊𝒏𝒈💍',
    '💞': '💞𝑽𝒂𝒍𝒆𝒏𝒕𝒊𝒏𝒆💞',
}

async def inlinequery(update: Update, context: CallbackContext) -> None:
    query = update.inline_query.query
    offset = int(update.inline_query.offset) if update.inline_query.offset else 0

    if query.startswith('collection.'):
        user_id, *search_terms = query.split(' ')[0].split('.')[1], ' '.join(query.split(' ')[1:])
        if user_id.isdigit():
            user_id = int(user_id)
            user = user_collection_cache.get(user_id) or await user_collection.find_one({'id': user_id})
            if user:
                user_collection_cache[user_id] = user
            all_characters = list({v['id']: v for v in user.get('characters', [])}.values()) if user else []
            if search_terms:
                regex = re.compile(' '.join(search_terms), re.IGNORECASE)
                all_characters = [
                    character for character in all_characters
                    if any(regex.search(field) for field in (character['name'], character['rarity'], character['id'], character['anime']))
                ]
        else:
            all_characters = []
    else:
        if query:
            regex = re.compile(query, re.IGNORECASE)
            all_characters = list(
                await collection.find({"$or": [{"name": regex}, {"rarity": regex}, {"id": regex}, {"anime": regex}]}).to_list(length=None)
            )
        else:
            all_characters = all_characters_cache.get('all_characters') or list(await collection.find({}).to_list(length=None))
            all_characters_cache['all_characters'] = all_characters

    # Pagination logic
    characters = all_characters[offset:offset + 50]
    next_offset = str(offset + 50) if len(characters) > 50 else str(offset + len(characters))

    results = []
    for character in characters:
        global_count = await user_collection.count_documents({'characters.id': character['id']})
        anime_characters = await collection.count_documents({'anime': character['anime']})

        if query.startswith('collection.'):
            user_character_count = sum(c['id'] == character['id'] for c in user.get('characters', []))
            user_anime_characters = sum(c['anime'] == character['anime'] for c in user.get('characters', []))
            caption = (
                f"<b>Lᴏᴏᴋ Aᴛ <a href='tg://user?id={user['id']}'>{escape(user.get('first_name', user['id']))}</a>'s Waifu....!!</b>\n\n"

f"<b>{character['id']}:</b> {character['name']} x{user_character_count}\n"
                f"<b>{character['anime']}</b> {user_anime_characters}/{anime_characters}\n"
                f"﹙<b>{character['rarity'][0]} 𝙍𝘼𝙍𝙄𝙏𝙔:</b> {character['rarity'][2:]}﹚\n"
            )
        else:
            caption = (
                f"<b>Lᴏᴏᴋ Aᴛ Tʜɪs Waifu....!!</b>\n\n"
                f"<b>{character['id']}:</b> {character['name']}\n"
                f"<b>{character['anime']}</b>\n"
                f"﹙<b>{character['rarity'][0]} 𝙍𝘼𝙍𝙄𝙏𝙔:</b> {character['rarity'][2:]}﹚\n\n"
            )

        # Create Inline Keyboard for Top 10 Grabbers for this specific character
        keyboard = [[InlineKeyboardButton("Top 10 Grabbers", callback_data=f'top10_grabbers_{character["id"]}')]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        # Append special tags if present
        for tag, description in tag_mappings.items():
            if tag in character['name']:
                caption += f"\n\n{description}"
                break

        results.append(
            InlineQueryResultPhoto(
                thumbnail_url=character['img_url'],
                id=f"{character['id']}_{time.time()}",
                photo_url=character['img_url'],
                caption=caption,
                reply_markup=reply_markup,
                parse_mode='HTML'
            )
        )

    await update.inline_query.answer(results, next_offset=next_offset, cache_time=5)

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(name)

async def top10_grabbers_callback(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()  # Acknowledge the callback

    # Extract character ID from callback data
    try:
        character_id = query.data.split('_')[2]
    except IndexError:
        grabbers_text = "Invalid callback data format."
        await query.edit_message_text(text=grabbers_text, parse_mode='HTML')
        return

    # Initialize the text for top grabbers
    grabbers_text = "An error occurred while fetching top grabbers."

    try:
        # Fetch the top 10 grabbers for this specific character
        top_grabbers = await user_collection.aggregate([
            {'$match': {'characters.id': character_id}},
            {'$unwind': '$characters'},
            {'$match': {'characters.id': character_id}},
            {'$group': {'_id': '$id', 'username': {'$first': '$username'}, 'first_name': {'$first': '$first_name'}, 'character_count': {'$sum': 1}}},
            {'$sort': {'character_count': -1}},
            {'$limit': 10}
        ]).to_list(length=10)

        if top_grabbers:
            grabbers_text = f"<b>Top 10 Grabbers for Character {character_id}:</b>\n\n"
            for i, user in enumerate(top_grabbers, start=1):
                username = user.get('username', 'Unknown') or 'Unknown'
                first_name = user.get('first_name', 'Unknown')
                
                # Ensure first_name is not None
                if first_name is None:
                    first_name = 'Unknown'
                
                first_name = html.escape(first_name)  # Safe to use now
                
                logger.debug(f"Username: {username}, First Name: {first_name}")

                if len(first_name) > 10:
                    first_name = first_name[:10] + '...'
                character_count = user.get('character_count', 0)
                grabbers_text += f'{i}. <a href="https://t.me/{username}"><b>{first_name}</b></a> ➾ <b>{character_count}</b>\n'
        else:
            grabbers_text = f"No grabbers found for Character {character_id}."

    except Exception as e:
        grabbers_text = f"An error occurred while fetching top grabbers: {str(e)}"
        logger.error(f"Exception occurred: {e}", exc_info=True)

# Edit the original message to show the top grabbers or the error message
    await query.edit_message_text(text=grabbers_text, parse_mode='HTML')

# Add the handlers to the application
application.add_handler(CallbackQueryHandler(top10_grabbers_callback, pattern=r'^top10_grabbers_'))
# Add inline query handler to the application
application.add_handler(InlineQueryHandler(inlinequery, block=False))