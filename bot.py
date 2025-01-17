import os
from telethon import TelegramClient
from pymongo import MongoClient
from config import API_ID, API_HASH, BOT_TOKEN, MONGO_URI

# Telegram client setup using Telethon
client = TelegramClient('bot', API_ID, API_HASH)

# Connect to MongoDB
mongo_client = MongoClient(MONGO_URI)
db = mongo_client['vote_database']  # MongoDB database name
votes_collection = db['votes']  # MongoDB collection name for votes

# Function to save a vote to MongoDB
def save_vote(user_id, vote_choice):
    votes_collection.insert_one({"user_id": user_id, "vote_choice": vote_choice})
    print(f"Vote saved for user: {user_id}, Choice: {vote_choice}")

# Start the bot with the provided bot token
async def main():
    await client.start(bot_token=BOT_TOKEN)
    print("Bot started successfully!")

    # Example of saving a vote when a user sends a message
    async for message in client.iter_messages('your_channel_or_group_name'):
        user_id = message.sender_id
        vote_choice = message.text  # Example, use a vote system here
        save_vote(user_id, vote_choice)

# Run the bot
client.loop.run_until_complete(main())
