#@flexdub_official
import random
from html import escape 

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext, CallbackQueryHandler, CommandHandler

from shivu import application, PHOTO_URL, SUPPORT_CHAT, UPDATE_CHAT, BOT_USERNAME, db, GROUP_ID

collection = db['total_pm_users']

async def start(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    first_name = update.effective_user.first_name
    username = update.effective_user.username

    user_data = await collection.find_one({"_id": user_id})

    if user_data is None:

        await collection.insert_one({"_id": user_id, "first_name": first_name, "username": username})

        await context.bot.send_message(chat_id=GROUP_ID, text=f"<a href='tg://user?id={user_id}'>{first_name}</a> STARTED THE BOT", parse_mode='HTML')
    else:

        if user_data['first_name'] != first_name or user_data['username'] != username:

            await collection.update_one({"_id": user_id}, {"$set": {"first_name": first_name, "username": username}})



    if update.effective_chat.type== "private":


        caption = f"""
     ***ʜᴇʟʟᴏ....💫  {escape(first_name)}



ᴡʜᴏ ᴀᴍ ɪ - ɪ'ᴍ*** [˹𝐆ʀᴀʙʙɪɴɢ 𝐘ᴏᴜʀ 𝐖ᴀɪғᴜ˼](https://t.me/Grabbing_Your_Waifu_Bot)

***◈ ━━━━━━━━ ● ━━━━━━━━ ◈

ᴀᴅᴅ ᴍᴇ ɪɴ ʏᴏᴜʀ ɢʀᴏᴜᴘ...✨️ ᴀɴᴅ ɪ ᴡɪʟʟ sᴇɴᴅ ʀᴀɴᴅᴏᴍ ᴄʜᴀʀᴀᴄᴛᴇʀs ᴀғᴛᴇʀ.. ᴇᴠᴇʀʏ 𝟷𝟶𝟶 ᴍᴇssᴀɢᴇs ɪɴ ɢʀᴏᴜᴘ.

──────────────────
✧⁠ COMMAND - ᴜsᴇ /ɢʀᴀʙ  ᴛᴏ ᴄᴏʟʟᴇᴄᴛ ᴛʜᴀᴛ ᴄʜᴀʀᴀᴄᴛᴇʀs ɪɴ ʏᴏᴜʀ ᴄᴏʟʟᴇᴄᴛɪᴏɴ ᴀɴᴅ sᴇᴇ ᴄᴏʟʟᴇᴄᴛɪᴏɴ ʙʏ ᴜsɪɴɢ /ʜᴀʀᴇᴍ ... sᴏ ᴀᴅᴅ ɪɴ ʏᴏᴜʀ ɢʀᴏᴜᴘ ᴀɴᴅ ᴄᴏʟʟᴇᴄᴛ ʏᴏᴜʀ ʜᴀʀᴇᴍ...✨️

◈ ━━━━━━━━ ● ━━━━━━━━ ◈***"""

        keyboard = [
            [InlineKeyboardButton("✤ ᴀᴅᴅ ᴍᴇ ✤", url=f'http://t.me/{BOT_USERNAME}?startgroup=new')],
            [InlineKeyboardButton("☊ 𝗌ᴜᴘᴘᴏʀᴛ ☊", url=f'https://t.me/{SUPPORT_CHAT}'),
            InlineKeyboardButton("✠ ᴜᴘᴅᴀᴛᴇ𝗌 ✠", url=f'https://t.me/{UPDATE_CHAT}')],
            [InlineKeyboardButton("✇ ʜᴇʟᴘ ✇", callback_data='help')],[InlineKeyboardButton("≎ ᴄʀᴇᴅɪᴛ ≎", url=f'https://t.me/{UPDATE_CHAT}')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        photo_url = random.choice(PHOTO_URL)

        await context.bot.send_photo(chat_id=update.effective_chat.id, photo=photo_url, caption=caption, reply_markup=reply_markup, parse_mode='markdown')

    else:
        photo_url = random.choice(PHOTO_URL)
        keyboard = [

            [InlineKeyboardButton("✇ ʜᴇʟᴘ ✇", callback_data='help'),
             InlineKeyboardButton("☊ 𝗌ᴜᴘᴘᴏʀᴛ ☊", url=f'https://t.me/{SUPPORT_CHAT}')],

        ]

        reply_markup = InlineKeyboardMarkup(keyboard)
        await context.bot.send_photo(chat_id=update.effective_chat.id, photo=photo_url, caption=f"""
{update.effective_user.first_name}                                                                                               """
                                     ,reply_markup=reply_markup )

async def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()

    if query.data == 'help':
        help_text = """
    ***Help Section :***
    
***/grab - to grabbed character (only works in group)***
***/fav - add your fav***
***/trade - to trade character***
***/gift - give any character from***
***/harem - to see your harem***
***/top - to see top users***
***/changetime - change character appear time***
    """ 
        help_keyboard = [[InlineKeyboardButton("⤂ʙᴀᴄᴋ", callback_data='back')]]
        reply_markup = InlineKeyboardMarkup(help_keyboard)

        await context.bot.edit_message_caption(chat_id=update.effective_chat.id, message_id=query.message.message_id, caption=help_text, reply_markup=reply_markup, parse_mode='markdown')

    elif query.data == 'back':

        caption = f"""
     ***ʜᴇʟʟᴏ....💫  {escape(first_name)}



ᴡʜᴏ ᴀᴍ ɪ - ɪ'ᴍ*** [˹𝐆ʀᴀʙʙɪɴɢ 𝐘ᴏᴜʀ 𝐖ᴀɪғᴜ˼](https://t.me/Grabbing_Your_Waifu_Bot)

***◈ ━━━━━━━━ ● ━━━━━━━━ ◈

ᴀᴅᴅ ᴍᴇ ɪɴ ʏᴏᴜʀ ɢʀᴏᴜᴘ...✨️ ᴀɴᴅ ɪ ᴡɪʟʟ sᴇɴᴅ ʀᴀɴᴅᴏᴍ ᴄʜᴀʀᴀᴄᴛᴇʀs ᴀғᴛᴇʀ.. ᴇᴠᴇʀʏ 𝟷𝟶𝟶 ᴍᴇssᴀɢᴇs ɪɴ ɢʀᴏᴜᴘ.

──────────────────
✧⁠ COMMAND - ᴜsᴇ /ɢʀᴀʙ  ᴛᴏ ᴄᴏʟʟᴇᴄᴛ ᴛʜᴀᴛ ᴄʜᴀʀᴀᴄᴛᴇʀs ɪɴ ʏᴏᴜʀ ᴄᴏʟʟᴇᴄᴛɪᴏɴ ᴀɴᴅ sᴇᴇ ᴄᴏʟʟᴇᴄᴛɪᴏɴ ʙʏ ᴜsɪɴɢ /ʜᴀʀᴇᴍ ... sᴏ ᴀᴅᴅ ɪɴ ʏᴏᴜʀ ɢʀᴏᴜᴘ ᴀɴᴅ ᴄᴏʟʟᴇᴄᴛ ʏᴏᴜʀ ʜᴀʀᴇᴍ...✨️

◈ ━━━━━━━━ ● ━━━━━━━━ ◈***"""

        keyboard = [
           [InlineKeyboardButton("✤ ᴀᴅᴅ ᴍᴇ ✤", url=f'http://t.me/{BOT_USERNAME}?startgroup=new')],
            [InlineKeyboardButton("☊ 𝗌ᴜᴘᴘᴏʀᴛ ☊", url=f'https://t.me/{SUPPORT_CHAT}'),
            InlineKeyboardButton("✠ ᴜᴘᴅᴀᴛᴇ𝗌 ✠", url=f'https://t.me/{UPDATE_CHAT}')],
            [InlineKeyboardButton("✇ ʜᴇʟᴘ ✇", callback_data='help')],[InlineKeyboardButton("≎ ᴄʀᴇᴅɪᴛ ≎", url=f'https://t.me/{UPDATE_CHAT}')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await context.bot.edit_message_caption(chat_id=update.effective_chat.id, message_id=query.message.message_id, caption=caption, reply_markup=reply_markup, parse_mode='markdown')

application.add_handler(CallbackQueryHandler(button, pattern='^help$|^back$', block=False))
start_handler = CommandHandler('start', start, block=False)
application.add_handler(start_handler)