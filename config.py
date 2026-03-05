import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
CHAT_ID = os.environ.get("CHAT_ID", "")
TIMEZONE = "Asia/Ho_Chi_Minh"

if not BOT_TOKEN:
    raise ValueError("❌ BOT_TOKEN chưa được cấu hình! Thêm vào file .env hoặc Railway Variables.")
if not CHAT_ID:
    raise ValueError("❌ CHAT_ID chưa được cấu hình! Thêm vào file .env hoặc Railway Variables.")
