import re
import time
from html import escape
from cachetools import TTLCache
from pymongo import ASCENDING
from telegram import Update, InlineQueryResultPhoto
from telegram.ext import InlineQueryHandler, CallbackContext
from shivu import user_collection, collection, application, db

# Setup MongoDB indexes
db.characters.create_index([('id', ASCENDING)])
db.characters.create_index([('anime', ASCENDING)])
db.characters.create_index([('img_url', ASCENDING)])

db.user_collection.create_index([('characters.id', ASCENDING)])
db.user_collection.create_index([('characters.name', ASCENDING)])
db.user_collection.create_index([('characters.img_url', ASCENDING)])

# Setup caching
all_characters_cache = TTLCache(maxsize=10000, ttl=36000)
user_collection_cache = TTLCache(maxsize=10000, ttl=60)

async def inlinequery(update: Update, context: CallbackContext) -> None:
    query = update.inline_query.query
    offset = int(update.inline_query.offset) if update.inline_query.offset else 0

    if query.startswith('collection.'):
        user_id, *search_terms = query.split(' ')[0].split('.')[1], ' '.join(query.split(' ')[1:])
        if user_id.isdigit():
            if user_id in user_collection_cache:
                user = user_collection_cache[user_id]
            else:
                user = await user_collection.find_one({'id': int(user_id)})
                if user:
                    user_collection_cache[user_id] = user

            all_characters = list({v['id']: v for v in user['characters']}.values()) if user else []
            if search_terms:
                regex = re.compile(' '.join(search_terms), re.IGNORECASE)
                all_characters = [
                    character for character in all_characters
                    if regex.search(character['name']) or regex.search(character['rarity']) or regex.search(character['id']) or regex.search(character['anime'])
                ]
        else:
            all_characters = []
    else:
        if query:
            regex = re.compile(query, re.IGNORECASE)
            all_characters = list(
                await collection.find({
                    "$or": [{"name": regex}, {"rarity": regex}, {"id": regex}, {"anime": regex}]
                }).to_list(length=None)
            )
        else:
            if 'all_characters' in all_characters_cache:
                all_characters = all_characters_cache['all_characters']
            else:
                all_characters = list(await collection.find({}).to_list(length=None))
                all_characters_cache['all_characters'] = all_characters

    # Pagination logic
    characters = all_characters[offset:offset + 50]
    next_offset = str(offset + 50) if len(characters) > 50 else str(offset + len(characters))

    results = []
    for character in characters:
        global_count = await user_collection.count_documents({'characters.id': character['id']})
        anime_characters = await collection.count_documents({'anime': character['anime']})

        if query.startswith('collection.'):
            user_character_count = sum(c['id'] == character['id'] for c in user['characters'])
            user_anime_characters = sum(c['anime'] == character['anime'] for c in user['characters'])
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
                f"<b>Gʟᴏʙᴀʟʟʏ Gʀᴀʙ {global_count} Times...</b>"
            )

        # Check for special tags in character's name
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
            '💞': '💞𝑽𝒂𝒍𝒆𝒏𝒕𝒊𝒏𝒆💞',
        }
        
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
                parse_mode='HTML'
            )
        )

    await update.inline_query.answer(results, next_offset=next_offset, cache_time=5)

# Add inline query handler to the application
application.add_handler(InlineQueryHandler(inlinequery, block=False))