# Import Pyrogram and Telethon
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from telethon import TelegramClient as TelethonClient, events
from telethon.tl.custom import Button
import asyncio
from config import API_ID, API_HASH, BOT_TOKEN

# Initialize Pyrogram Client (for /start and voting features)
pyrogram_bot = Client("VoteBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Initialize Telethon Client (for video and group join features)
telethon_client = TelethonClient('bot', API_ID, API_HASH)

# Store votes in a dictionary
votes = {}

# Pyrogram: Start Command
@pyrogram_bot.on_message(filters.command("start"))
async def start(_, message):
    await message.reply_text(
        "**Welcome to the Voting Bot!**\n\nUse /vote to create a new vote.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Create a Vote", callback_data="create_vote")]
        ])
    )

# Pyrogram: Create Poll
@pyrogram_bot.on_callback_query(filters.regex("create_vote"))
async def create_vote(_, query):
    await query.message.edit_text(
        "Send me the **poll question** (e.g., 'Which is your favorite color?')."
    )

    # Wait for response
    poll_question = await pyrogram_bot.listen(query.message.chat.id)

    # Store question
    chat_id = query.message.chat.id
    votes[chat_id] = {"question": poll_question.text, "options": {}, "voters": {}}

    await query.message.reply_text(
        "Now send **poll options** one by one.\nSend 'done' when finished."
    )

    while True:
        option = await pyrogram_bot.listen(query.message.chat.id)
        if option.text.lower() == "done":
            break
        votes[chat_id]["options"][option.text] = 0

    await query.message.reply_text(
        "**Poll Created Successfully!**\n\nNow use /vote to start voting."
    )

# Pyrogram: Start Voting
@pyrogram_bot.on_message(filters.command("vote"))
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

# Pyrogram: Handle Voting
@pyrogram_bot.on_callback_query(filters.regex("^vote_"))
async def handle_vote(_, query):
    chat_id = query.message.chat.id
    user_id = query.from_user.id

    if user_id in votes[chat_id]["voters"]:
        await query.answer("You have already voted!", show_alert=True)
        return

    option = query.data.split("_", 1)[1]
    votes[chat_id]["options"][option] += 1
    votes[chat_id]["voters"][user_id] = option

    # Update poll
    buttons = [
        [InlineKeyboardButton(f"{opt} ({count})", callback_data=f"vote_{opt}")]
        for opt, count in votes[chat_id]["options"].items()
    ]

    await query.message.edit_text(
        f"**{votes[chat_id]['question']}**\n\nVote below:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

    await query.answer("Vote counted!")

# Telethon: Send Welcome Message with Video and Buttons
async def send_welcome_message(event):
    # Video URL (MP4)
    video_url = 'https://files.catbox.moe/xdo3pd.mp4'  # Your video URL

    # Button to show after video with a link
    button = [
        [Button.inline("Click Me!", data="button_click")],  # Inline button
        [Button.url("Join Our Group", "https://t.me/+1WQ8gB5cgHs0ZDg1")]  # Button with URL
    ]

    # Send video with button
    await event.reply(
        "Welcome to the vote bot! Here's a video:",
        file=video_url,  # Video file (can be URL or local file path)
        buttons=button
    )

# Telethon: Handle /start Command
@telethon_client.on(events.NewMessage(pattern='/start'))
async def handler(event):
    await send_welcome_message(event)

# Start the Pyrogram Bot
async def pyrogram_main():
    await pyrogram_bot.start()
    print("Pyrogram bot started successfully!")

# Start the Telethon Bot
async def telethon_main():
    await telethon_client.start(bot_token=BOT_TOKEN)
    print("Telethon bot started successfully!")
    await telethon_client.run_until_disconnected()

# Run Both Bots
async def main():
    await asyncio.gather(
        pyrogram_main(),
        telethon_main()
    )

# Run the bots
asyncio.run(main())
