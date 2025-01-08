from telethon import TelegramClient, events
import re

# Your API ID and Hash from https://my.telegram.org
API_ID = 155  # Replace with your API ID
API_HASH = "92734bf4[...]3e396ec66fa"  # Replace with your API Hash

# Main target group/channel to forward messages to
MAIN_TARGET_GROUP = 2260267566  # Replace with your target group ID

# List of allowed users (usernames)
ALLOWED_USERS = ["SoliditySam", "User2", "User3"]

# List of groups/channels to monitor (by ID)
MONITORED_GROUPS = [4796838775,2260267566]  # Replace with the specific group/channel IDs

# Regex patterns for EVM and Solana addresses
EVM_ADDRESS_REGEX = r"0x[a-fA-F0-9]{40}"  # EVM addresses
SOLANA_ADDRESS_REGEX = r"[1-9A-HJ-NP-Za-km-z]{32,44}"  # Solana addresses

# Initialize the Telegram client
client = TelegramClient("session", API_ID, API_HASH)



@client.on(events.NewMessage)
async def monitor_messages(event):
    # Get chat and sender details
    chat = await event.get_chat()
    sender = await event.get_sender()
    message_text = event.message.message if event.message else ""

    

    # Extract details
    chat_id = chat.id
    chat_title = chat.title if hasattr(chat, "title") else "Unknown Chat"
    sender_username = sender.username if sender.username else None

    # Check if the chat is in the monitored groups list
    if chat_id in MONITORED_GROUPS:
        # Determine if the message is from a channel or a user
        if isinstance(sender, type(chat)):  # If sender is the same as chat (channel message)
            sender_name = chat_title
        else:
            sender_name = sender_username

        # Check if the sender is authorized
        if sender_username and sender_username not in ALLOWED_USERS:
            print(f"Unauthorized user @{sender_username} in {chat_title}.")
            return

        # Look for EVM or Solana addresses in the message
        evm_matches = re.findall(EVM_ADDRESS_REGEX, message_text)
        solana_matches = re.findall(SOLANA_ADDRESS_REGEX, message_text)

        # If any matches are found, forward the message
        if evm_matches or solana_matches:
            # Debugging information
            print(f"Debug Sender: {sender}")
            print(f"Debug Chat: {chat}")
            try:
                await client.send_message(
                    MAIN_TARGET_GROUP,
                    f"🔔 Forwarded message from {sender_name} in {chat_title}:\n\n{message_text}",
                )
                print(f"Message forwarded from to target group. {sender_name} in {chat_title}:\n\n{message_text}")
            except Exception as e:
                print(f"Failed to forward message: {e}")
    else:
        print(f"Ignored message from unmonitored chat ID {chat_id} ({chat_title}).")


def main():
    print("Starting Telegram monitoring...")
    # Start the client
    with client:
        client.run_until_disconnected()


if __name__ == "__main__":
    main()
