import io
import sys
import traceback
from contextlib import redirect_stdout
from subprocess import getoutput as run
from pyrogram import filters, Client
from shivu import shivuu as bot
from datetime import datetime

DEV_LIST = [6584789596, 2010819209, 6154972031, 7185106962]

MAX_CAPTION_LENGTH = 1024

async def aexec(code, client, message):
    exec(
        "async def __aexec(client, message): "
        + "".join(f"\n {l_}" for l_ in code.split("\n"))
    )
    return await locals()["__aexec"](client, message)

@bot.on_message(filters.command(["run", "eval"], ["?","!",".","*","/","$",]))
async def eval(client, message):
    if message.from_user.id not in DEV_LIST:
        return await message.reply_text("You Don't Have Enough Rights To Run This!")
    
    if len(message.text.split()) < 2:
        return await message.reply_text("Input Not Found!")
    
    status_message = await message.reply_text("Processing ...")
    cmd = message.text.split(None, 1)[1]
    start = datetime.now()
    reply_to_ = message.reply_to_message or message

    old_stderr = sys.stderr
    old_stdout = sys.stdout
    redirected_output = sys.stdout = io.StringIO()
    redirected_error = sys.stderr = io.StringIO()
    stdout, stderr, exc = None, None, None

    try:
        await aexec(cmd, client, message)
    except Exception:
        exc = traceback.format_exc()

    stdout = redirected_output.getvalue()
    stderr = redirected_error.getvalue()
    sys.stdout = old_stdout
    sys.stderr = old_stderr

    evaluation = exc or stderr or stdout or "Success"
    end = datetime.now()
    ping = (end - start).microseconds / 1000

    final_output = (
        "<b>📎 Input</b>: "
        f"<code>{cmd}</code>\n\n"
        "<b>📒 Output</b>:\n"
        f"<code>{evaluation.strip()}</code>\n\n"
        f"<b>✨ Taken Time</b>: {ping}<b>ms</b>"
    )

    if len(final_output) > 4096:
        with io.BytesIO(str.encode(final_output)) as out_file:
            out_file.name = "eval.text"
            caption = cmd[:MAX_CAPTION_LENGTH]  # Truncate the caption if it's too long
            await reply_to_.reply_document(
                document=out_file, caption=caption, disable_notification=True
            )
    else:
        await status_message.edit_text(final_output)

@bot.on_message(filters.command(["sh", "shell"], ["?","!",".","*","/","$",]))
async def sh(client, message):
    if message.from_user.id != 6584789596:
        return await message.reply_text("You Don't Have Enough Rights To Run This!")
    
    code = message.text.split(" ", 1)[1] if len(message.text.split()) > 1 else ""
    if not code:
        return await message.reply_text("No Input Found!")
    
    x = run(code)
    string = f"📎 Input: {code}\n\n📒 Output:\n{x}"

    try:
        await message.reply_text(string)
    except Exception as e:
        with io.BytesIO(str.encode(string)) as out_file:
            out_file.name = "shell.text"
            caption = str(e)[:MAX_CAPTION_LENGTH]  # Truncate the caption if it's too long
            await message.reply_document(document=out_file, caption=caption)