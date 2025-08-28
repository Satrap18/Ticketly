import sys
import os
import logging

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "website.settings")

import django
django.setup()

from accounts.models import CustomUserModel
from telegram.ext import ApplicationBuilder, CommandHandler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = "7077726700:AAEQVdll2qPcUoGebLHjBPa00tA6J_puYns"

async def start(update, context):
    await update.message.reply_text("Hello! The robot turned on")

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))

if __name__ == "__main__":
    app.run_polling()
