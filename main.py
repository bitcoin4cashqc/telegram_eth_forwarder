from telethon import TelegramClient, events, Button
import re
import os
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Fetch configuration from .env file
API_ID = int(os.getenv("API_ID"))  # Telegram API ID
API_HASH = os.getenv("API_HASH")  # Telegram API Hash
BOT_TOKEN = os.getenv("BOT_TOKEN")  # Bot token
BOT_ID = int(os.getenv("BOT_ID"))
MAIN_TARGET_GROUP = os.getenv("MAIN_TARGET_GROUP") # Target group/channel ID for forwarding

MONITORED_GROUPS = [
    int(group) if group.isdigit() else group
    for group in os.getenv("MONITORED_GROUPS").split(",")
]
LINKS = json.loads(os.getenv("LINKS"))  # Links dictionary loaded from .env
ADMIN_ID = int(os.getenv("ADMIN_ID"))


# Regex patterns for EVM and Solana addresses
EVM_ADDRESS_REGEX = r"0x[a-fA-F0-9]{40}"  # EVM (Ethereum) address pattern
SOLANA_ADDRESS_REGEX = r"[1-9A-HJ-NP-Za-km-z]{32,44}"  # Solana address pattern

# Initialize Telegram clients
personal_client = TelegramClient("personal_session", API_ID, API_HASH)
bot_client = TelegramClient("bot_session", API_ID, API_HASH).start(bot_token=BOT_TOKEN)


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
    Personal listener to monitor messages and forward raw messages to the bot.
    """
    chat = await event.get_chat()
    sender = await event.get_sender()
    message_text = event.message.message if event.message else ""
    print(chat)
    print(sender)
    print(message_text)
    chat_id = chat.id
    chat_title = chat.title if hasattr(chat, "title") else "Unknown Chat"
    sender_username = sender.username if sender.username else None
    print(chat_id)
    print(chat_title)

    
    # Process messages only from monitored groups
    if (chat_id in MONITORED_GROUPS or chat_title in MONITORED_GROUPS):
        evm_matches = re.findall(EVM_ADDRESS_REGEX, message_text)
        solana_matches = re.findall(SOLANA_ADDRESS_REGEX, message_text)

        if evm_matches or solana_matches:
            try:
                target_entity = await personal_client.get_input_entity(BOT_ID)
                target_entity = await personal_client.get_entity(target_entity)

                await personal_client.send_message(
                    target_entity,
                    f"🔔 Forwarded message from {chat_title}:\n\n{message_text}"
                )
                print(f"Message forwarded to bot from {chat_title}: {message_text}")
            except Exception as e:
                print(f"Failed to forward message to bot: {e}")
        else:
            print(f"No valid address found in the message: {message_text}")
    else:
        print(f"Ignored message from unmonitored chat ID {chat_id} ({chat_title}).")


@bot_client.on(events.NewMessage)
async def bot_listener(event):
    """
    Bot listener to process messages from the personal client, format them, and forward to the main group.
    """
    sender = await event.get_sender()
    sender_username = sender.username if sender.username else None

    # Only process messages forwarded from the personal client
    if sender.id != ADMIN_ID:
        print("not admin")
        return
    
    # Check if the message is a forwarded message
    if event.message.forward:
        print(f"Ignored forwarded message: {event.message.message}")
        return

    message_text = event.message.message if event.message else ""
    evm_matches = re.findall(EVM_ADDRESS_REGEX, message_text)
    solana_matches = re.findall(SOLANA_ADDRESS_REGEX, message_text)

    if evm_matches or solana_matches:
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
    else:
        await event.reply("No valid address found in the message.")


def main():
    """
    Main function to run both personal and bot listeners.
    """
    print("Starting personal and bot listeners...")
    with personal_client, bot_client:
        personal_client.run_until_disconnected()
        bot_client.run_until_disconnected()


if __name__ == "__main__":
    main()
