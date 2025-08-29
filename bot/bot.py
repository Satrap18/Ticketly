import sys
import os
import logging

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "website.settings")

import django
django.setup()

from accounts.models import CustomUserModel
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler, MessageHandler, ConversationHandler, filters, Application,CallbackContext

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = "7077726700:AAEQVdll2qPcUoGebLHjBPa00tA6J_puYns"

ACCOUNT = range(1)

async def start(update, context):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    fullname = update.message.from_user.full_name 
    await update.message.reply_text(f"Hello {fullname}, welcome to the ticket robot")
    keyboard = [['Login'], ['Signup']]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await context.bot.send_message(chat_id=chat_id,
                                   text='Please choose:',
                                   reply_markup=reply_markup)

    return ACCOUNT

async def account(update, context):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id

    if update.message.text == 'Login':
        await context.bot.send_message(chat_id, 'You Select Login')
    elif update.message.text == 'Signup':
        await context.bot.send_message(chat_id, 'You Select Signup')
    else:
        await context.bot.send_message(chat_id, 'Please Select True Options!')


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text('cancelled!')
    return ConversationHandler.END

def main():
    application = ApplicationBuilder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            ACCOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, account)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
        )
    
    application.add_handler(conv_handler)
    application.run_polling()

if __name__ == '__main__':
    main()
    