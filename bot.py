from telethon import TelegramClient, events
from telethon.tl.custom import Button
from config import API_ID, API_HASH, BOT_TOKEN

# Telegram Client Setup
client = TelegramClient('bot', API_ID, API_HASH)

# Bot Start Function
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

# Handling /start command
@client.on(events.NewMessage(pattern='/start'))
async def handler(event):
    await send_welcome_message(event)

# Start the bot with the provided bot token
async def main():
    await client.start(bot_token=BOT_TOKEN)
    print("Bot started successfully!")
    await client.run_until_disconnected()

# Run the bot
client.loop.run_until_complete(main())
