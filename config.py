import os
from dotenv import load_dotenv

load_dotenv()
API_TOKEN = os.getenv('BOT_TOKEN')
DB_NAME = 'quiz_bot.db'