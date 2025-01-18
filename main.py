from telethon import TelegramClient, events, Button
import re
import os
import json
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Fetch configuration from .env file
API_ID = int(os.getenv("API_ID"))  # Telegram API ID
API_HASH = os.getenv("API_HASH")  # Telegram API Hash
BOT_TOKEN = os.getenv("BOT_TOKEN")  # Bot token
MAIN_TARGET_GROUP = int(os.getenv("MAIN_TARGET_GROUP"))  # Target group/channel ID for forwarding

MONITORED_GROUPS = [
    int(group) if group.isdigit() else group
    for group in os.getenv("MONITORED_GROUPS").split(",")
]
LINKS = json.loads(os.getenv("LINKS"))  # Links dictionary loaded from .env
ALLOWED_USERS = [
    int(user) if user.isdigit() else user
    for user in os.getenv("ALLOWED_USERS", "").split(",")
]

# Regex patterns for EVM and Solana addresses
EVM_ADDRESS_REGEX = r"0x[a-fA-F0-9]{40}"  # EVM (Ethereum) address pattern
SOLANA_ADDRESS_REGEX = r"[1-9A-HJ-NP-Za-km-z]{32,44}"  # Solana address pattern

# Initialize Telegram clients
personal_client = TelegramClient("personal_session", API_ID, API_HASH)
bot_client = TelegramClient("bot_session", API_ID, API_HASH).start(bot_token=BOT_TOKEN)

# Buffer to store messages
message_buffer = []

# Lock to synchronize access to the buffer
buffer_lock = asyncio.Lock()

def format_button_links(address, address_suffix):
    """
    Format inline buttons with given address and suffix.

    Args:
        address (str): Address to include in the links.
        address_suffix (str): "_ETH" or "_SOL" to append to the address.

    Returns:
        list: List of formatted inline buttons.
    """
    return [
        Button.url(key, url.replace("data", address + address_suffix) if "BitFootBot" in key else url.replace("data", address))
        for key, url in LINKS.items()
    ]

@personal_client.on(events.NewMessage)
async def personal_listener(event):
    """
    Personal listener to monitor messages and store them in the buffer.
    """
    chat = await event.get_chat()
    sender = await event.get_sender()
    message_text = event.message.message if event.message else ""

    chat_id = chat.id
    chat_title = chat.title if hasattr(chat, "title") else "Unknown Chat"
    sender_id = sender.id if sender else "anonymous"
    sender_username = sender.username if sender else "anonymous"
    
    # Check if the message is from monitored groups and the sender is allowed
    if (chat_id in MONITORED_GROUPS or chat_title in MONITORED_GROUPS) and (
        sender_id in ALLOWED_USERS or sender_username in ALLOWED_USERS
    ):
        evm_matches = re.findall(EVM_ADDRESS_REGEX, message_text)
        solana_matches = re.findall(SOLANA_ADDRESS_REGEX, message_text)

        if evm_matches or solana_matches:
            async with buffer_lock:
                message_buffer.append({
                    "chat_title": chat_title,
                    "message_text": message_text,
                    "evm_matches": evm_matches,
                    "solana_matches": solana_matches,
                })
                print(f"Message buffered from {chat_title}: {message_text}")
        else:
            print(f"No valid address found in the message: {message_text}")
    else:
        print(f"Ignored message from unmonitored chat ID {chat_id} ({chat_title}) or unauthorized sender.")

async def process_buffered_messages():
    """
    Periodic task to process buffered messages and send them via the bot.
    """
    while True:
        async with buffer_lock:
            if message_buffer:
                messages_to_process = message_buffer[:]
                message_buffer.clear()
            else:
                messages_to_process = []

        for message in messages_to_process:
            chat_title = message["chat_title"]
            message_text = message["message_text"]
            evm_matches = message["evm_matches"]
            solana_matches = message["solana_matches"]

            # Determine address type
            address = evm_matches[0] if evm_matches else solana_matches[0]
            address_suffix = "_ETH" if evm_matches else "_SOL"

            # Generate inline buttons
            buttons = format_button_links(address, address_suffix)

            # Forward the message with buttons to the main target group
            try:
                target_entity_bot = await bot_client.get_input_entity(MAIN_TARGET_GROUP)
                target_entity_bot = await bot_client.get_entity(target_entity_bot)
                await bot_client.send_message(
                    target_entity_bot,
                    f"{message_text}",
                    buttons=buttons,
                    link_preview=False
                )
                print(f"Message forwarded to main group: {message_text}")
            except Exception as e:
                print(f"Failed to forward message to main group: {e}")

        await asyncio.sleep(5)  # Sleep before checking the buffer again

def main():
    """
    Main function to run both personal and bot listeners.
    """
    print("Starting personal and bot listeners...")
    loop = asyncio.get_event_loop()
    loop.create_task(process_buffered_messages())
    with personal_client, bot_client:
        personal_client.run_until_disconnected()
        bot_client.run_until_disconnected()

if __name__ == "__main__":
    main()
