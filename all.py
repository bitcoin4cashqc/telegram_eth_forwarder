from telethon import TelegramClient, events
import re
import os

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Fetch configuration from .env file
API_ID = int(os.getenv("API_ID"))  # Telegram API ID
API_HASH = os.getenv("API_HASH")  # Telegram API Hash

# Initialize Telegram clients
personal_client = TelegramClient("personal_session", API_ID, API_HASH)

@personal_client.on(events.NewMessage)
async def personal_listener(event):
    """
    Personal listener to monitor messages and store them in the buffer.
    """
    chat = await event.get_chat()
   
    message_text = event.message.message if event.message else ""

    print(chat)
    print(event.message)

   
def main():
    """
    Main function to run both personal and bot listeners.
    """
    print("Starting personal...")
   
    with personal_client:
        personal_client.run_until_disconnected()
      

if __name__ == "__main__":
    main()
