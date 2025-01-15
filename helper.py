from telethon import TelegramClient
from dotenv import load_dotenv
import os
import asyncio

# Load environment variables
load_dotenv()

# Fetch configuration from .env file
API_ID = int(os.getenv("API_ID"))  # Telegram API ID
API_HASH = os.getenv("API_HASH")  # Telegram API Hash

# Initialize Telegram client
client = TelegramClient("helper_session", API_ID, API_HASH)

async def search_dialogs_by_name(client, search_name):
    """
    Search dialogs (chats, groups, and channels) by name.

    Args:
        client (TelegramClient): The initialized Telethon client.
        search_name (str): The name to search for.
    """
    dialogs = await client.get_dialogs()
    matching_dialogs = [dialog for dialog in dialogs if search_name.lower() in dialog.name.lower() and not dialog.archived]

    if not matching_dialogs:
        print(f"No dialogs found matching the name: {search_name}")
        return

    print(f"Found {len(matching_dialogs)} dialogs matching the name '{search_name}':")

    for index, dialog in enumerate(matching_dialogs, start=1):
        dialog_type = "User" if dialog.is_user else "Group" if dialog.is_group else "Channel"
        print(f"{index}. [{dialog_type}] {dialog.name} (ID: {dialog.id})")

    user_input = input("Enter a number to view details of a specific dialog, or 'q' to quit: ").strip().lower()

    if user_input.isdigit():
        dialog_index = int(user_input) - 1
        if 0 <= dialog_index < len(matching_dialogs):
            await show_dialog_details(matching_dialogs[dialog_index])
        else:
            print("Invalid dialog number. Please try again.")
    elif user_input == "q":
        print("Exiting search.")
    else:
        print("Invalid input. Please try again.")

async def show_dialog_details(dialog):
    """
    Display detailed information about a specific dialog.

    Args:
        dialog (Dialog): The dialog object to display details for.
    """
    dialog_type = "User" if dialog.is_user else "Group" if dialog.is_group else "Channel"
    print("\nDialog Details:")
    print(f"  Name: {dialog.name}")
    print(f"  ID: {dialog.id}")
    print(f"  Type: {dialog_type}")

    print("\nFetching recent messages...")
    async for message in client.iter_messages(dialog.id, limit=5):
        sender = await message.get_sender()
        sender_name = sender.username if sender and sender.username else "Unknown"
        print(f"  From: {sender_name} | Message: {message.text}")

async def main():
    """
    Main function to search for dialogs by name.
    """
    print("Connecting to Telegram...")
    await client.start()

    try:
        search_name = input("Enter the name of the group/channel to search for: ").strip()
        await search_dialogs_by_name(client, search_name)
    finally:
        await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
