import time
import asyncio
from datetime import datetime
from pyrogram import Client, filters
from pyrogram.errors import BadMsgNotification
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import API_ID, API_HASH, BOT_TOKEN

# Sync system time with Telegram servers
async def sync_time():
    while True:
        try:
            async with Client("TimeSyncBot", api_id=API_ID, api_hash=API_HASH) as temp_bot:
                await temp_bot.send_message("me", f"Server Time Sync: {datetime.utcnow()}")
                print("✅ Time Sync Successful!")
                break
        except Exception as e:
            print(f"⏳ Retrying Time Sync... {e}")
            await asyncio.sleep(5)  # Wait for 5 seconds before retrying

# Initialize bot client
bot = Client("VoteBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Store votes in a dictionary
votes = {}

# Start Command
@bot.on_message(filters.command("start"))
async def start(_, message):
    try:
        await message.reply_text(
            "**Welcome to the Voting Bot!**\n\nUse /vote to create a new vote.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Create a Vote", callback_data="create_vote")]
            ])
        )
    except BadMsgNotification:
        print("⏳ Time sync error, retrying...")
        await asyncio.sleep(5)
        await start(_, message)

# Create a new poll
@bot.on_callback_query(filters.regex("create_vote"))
async def create_vote(_, query):
    try:
        await query.message.edit_text(
            "Send me the **poll question** (e.g., 'Which is your favorite color?')."
        )

        poll_question = await bot.listen(query.message.chat.id)

        chat_id = query.message.chat.id
        votes[chat_id] = {"question": poll_question.text, "options": {}, "voters": {}}

        await query.message.reply_text(
            "Now send **poll options** one by one.\nSend 'done' when finished."
        )

        while True:
            option = await bot.listen(query.message.chat.id)
            if option.text.lower() == "done":
                break
            votes[chat_id]["options"][option.text] = 0

        await query.message.reply_text(
            "**Poll Created Successfully!**\n\nNow use /vote to start voting."
        )
    except BadMsgNotification:
        print("⏳ Time sync error, retrying...")
        await asyncio.sleep(5)
        await create_vote(_, query)

# Start voting
@bot.on_message(filters.command("vote"))
async def start_voting(_, message):
    chat_id = message.chat.id

    if chat_id not in votes or not votes[chat_id]["options"]:
        await message.reply_text("No active poll. Use /start to create one.")
        return

    buttons = [
        [InlineKeyboardButton(f"{option} ({count})", callback_data=f"vote_{option}")]
        for option, count in votes[chat_id]["options"].items()
    ]

    await message.reply_text(
        f"**{votes[chat_id]['question']}**\n\nVote below:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

# Handle voting
@bot.on_callback_query(filters.regex("^vote_"))
async def handle_vote(_, query):
    chat_id = query.message.chat.id
    user_id = query.from_user.id

    if user_id in votes[chat_id]["voters"]:
        await query.answer("You have already voted!", show_alert=True)
        return

    option = query.data.split("_", 1)[1]
    votes[chat_id]["options"][option] += 1
    votes[chat_id]["voters"][user_id] = option

    buttons = [
        [InlineKeyboardButton(f"{opt} ({count})", callback_data=f"vote_{opt}")]
        for opt, count in votes[chat_id]["options"].items()
    ]

    await query.message.edit_text(
        f"**{votes[chat_id]['question']}**\n\nVote below:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

    await query.answer("Vote counted!")

# Run bot with time sync
async def main():
    await sync_time()  # Sync time before running the bot
    bot.run()

asyncio.run(main())
