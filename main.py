from telethon import TelegramClient, events
import re
import os
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Fetch configuration from .env file
API_ID = int(os.getenv("API_ID"))  # Telegram API ID
API_HASH = os.getenv("API_HASH")  # Telegram API Hash
MAIN_TARGET_GROUP = int(os.getenv("MAIN_TARGET_GROUP"))  # Target group/channel ID for forwarding
ALLOWED_USERS = [
    int(user) if user.isdigit() else user
    for user in os.getenv("ALLOWED_USERS").split(",")
]
MONITORED_GROUPS = [
    int(group) if group.isdigit() else group
    for group in os.getenv("MONITORED_GROUPS").split(",")
]
LINKS = json.loads(os.getenv("LINKS"))  # Links dictionary loaded from .env

# Regex patterns for EVM and Solana addresses
EVM_ADDRESS_REGEX = r"0x[a-fA-F0-9]{40}"  # EVM (Ethereum) address pattern
SOLANA_ADDRESS_REGEX = r"[1-9A-HJ-NP-Za-km-z]{32,44}"  # Solana address pattern

# Initialize the Telegram client
client = TelegramClient("session", API_ID, API_HASH)


def formatLink(key, url, data):
    """
    Format a single link by replacing the 'data' placeholder with the provided data value.

    Args:
        key (str): The description of the link (e.g., "Buy On BitFootBot").
        url (str): The URL template containing the 'data' placeholder.
        data (str): The value to replace 'data' in the URL.

    Returns:
        str: A formatted link as a Markdown-compatible string.
    """
    formatted_url = url.replace("data", data)  # Replace the placeholder in the URL
    formatted_link = f"[{key}]({formatted_url})\n\n"  # Format the link with Markdown
    return formatted_link


@client.on(events.NewMessage)
async def monitor_messages(event):
    """
    Monitor incoming messages in specified groups and process them.

    Args:
        event (telethon.events.NewMessage.Event): The event triggered by a new message.
    """
    # Extract chat and sender details
    chat = await event.get_chat()
    sender = await event.get_sender()
    message_text = event.message.message if event.message else ""

    # Extract chat and sender metadata
    chat_id = chat.id
    chat_title = chat.title if hasattr(chat, "title") else "Unknown Chat"
    sender_username = sender.username if sender.username else None

    # Check if the chat is in the monitored groups list by name or ID
    if chat_id in MONITORED_GROUPS or chat_title in MONITORED_GROUPS:
        # Determine if the sender is a user or a channel
        sender_name = chat_title if isinstance(sender, type(chat)) else sender_username

        # Verify if the sender is allowed by username or user ID
        sender_id = sender.id
        if sender_username and sender_username not in ALLOWED_USERS and sender_id not in ALLOWED_USERS:
            print(f"Unauthorized user @{sender_username} (ID: {sender_id}) in {chat_title} (ID: {chat_id}).")
            return

        # Look for EVM or Solana addresses in the message
        evm_matches = re.findall(EVM_ADDRESS_REGEX, message_text)
        solana_matches = re.findall(SOLANA_ADDRESS_REGEX, message_text)

       # Inside monitor_messages function:
        if evm_matches or solana_matches:
            try:
                # Extract the first match and determine the type
                address = None
                links_msg = ""

                if evm_matches:
                    address = evm_matches[0]
                elif solana_matches:
                    address = solana_matches[0]

                # Build the links message
                for key, url in LINKS.items():  # Ensure you use .items() to iterate over dictionary
                    if "BitFootBot" in key:
                        if evm_matches:
                            links_msg += formatLink(key, url, address + "_ETH")
                        elif solana_matches:
                            links_msg += formatLink(key, url, address + "_SOL")
                    else:
                        links_msg += formatLink(key, url, address)

                target_entity = await client.get_entity(MAIN_TARGET_GROUP)
                # Send the formatted message to the target group
                print(links_msg)
                await client.send_message(
                    target_entity,
                    f"🔔 Forwarded message from {sender_name} in {chat_title}:\n\n{message_text}\n\n{links_msg}",
                    link_preview=False
                )
                print(f"Message forwarded with address {address} from {sender_name} in {chat_title}:\n\n{message_text}")

            except Exception as e:
                print(f"Failed to forward message: {e}")
        else:
            print(f"No valid address found in the message: {message_text}")
    else:
        print(f"Ignored message from unmonitored chat ID {chat_id} ({chat_title}).")


def main():
    """
    Main function to start the Telegram monitoring bot.
    """
    print("Starting Telegram monitoring...")
    # Start the Telegram client
    with client:
        client.run_until_disconnected()


if __name__ == "__main__":
    main()
