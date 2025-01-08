
# Telegram ETH Forwarder

This project is a Telegram message forwarder that monitors specific groups or channels for messages containing Ethereum (EVM) or Solana addresses and forwards those messages to a designated group.

## Features
- Monitors specific groups or channels.
- Filters messages for Ethereum (EVM) and Solana wallet addresses.
- Processes messages from allowed users (for groups).
- Forwards relevant messages to a specified target group or channel.

## Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/your-repository.git
cd telegram_eth_forwarder
```

### 2. Create a Virtual Environment
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Required Dependencies
```bash
pip install -r requirements.txt
```

### 4. Fix `_ctypes` Module Error (if needed)
If you encounter a `ModuleNotFoundError: No module named '_ctypes'`, install the necessary system dependencies:

#### On Ubuntu/Debian
```bash
sudo apt update
sudo apt install libffi-dev
```

#### On Fedora
```bash
sudo dnf install libffi-devel
```

#### On Arch
```bash
sudo pacman -S libffi
```

After installing the dependencies, reinstall Python if necessary.

#### Using `pyenv`
```bash
pyenv uninstall 3.12.3
pyenv install 3.12.3
pyenv global 3.12.3
```

Recreate your virtual environment:
```bash
rm -rf .venv
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 5. Configure the Script

1. Obtain your **API ID** and **API Hash** from [Telegram API Development Tools](https://my.telegram.org/auth).
2. Update the `main.py` file with:
   - Your **API ID** and **API Hash**.
   - The list of groups or channels you want to monitor (`MONITORED_GROUPS`).
   - The usernames of allowed users (`ALLOWED_USERS`).
   - The target group or channel ID for forwarding messages (`MAIN_TARGET_GROUP`).

### 6. Run the Script
```bash
python main.py
```

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.