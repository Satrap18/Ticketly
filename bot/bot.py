import sys
import os
import logging
import requests

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

ACCOUNT, LOGIN, SINGUP, USERNAME, PASSWORD, MAIN_HANDLER = range(6)
token_cache = {}

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

# Account Handler #

async def account(update, context):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id

    if update.message.text == 'Login':
        await context.bot.send_message(chat_id, 'Your Username Account:')
        return USERNAME

    elif update.message.text == 'Signup':
        await context.bot.send_message(chat_id, 'You Select Signup')
    else:
        await context.bot.send_message(chat_id, 'Please Select True Options!')

# End Account Handler #

# Login #
async def login_username(update, context):
    context.user_data["username"] = update.message.text
    await update.message.reply_text("Your Password Account:")
    return PASSWORD

async def login_password(update, context):
    user_id = update.effective_user.id
    password = update.message.text
    username = context.user_data["username"]

    try:
        await update.message.delete()
        await context.bot.send_message(user_id, 'please wait...')
    except Exception as e:
        print("Could not delete message:", e)

    success, token = login_and_cache(user_id, username, password)

    if success:
        keyboard = [['Ticket'], ['Logout']]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

        await update.message.reply_text("✅ Login successful!")
        await update.message.reply_text("Please choose:", reply_markup=reply_markup)
        return MAIN_HANDLER
    elif not success:
        await update.message.reply_text("❌ Login failed. Check username/password.")
        await account(update, context)
        return ACCOUNT
    else:
        await update.message.reply_text('Try Again Later!')

def login_and_cache(user_id, username, password):
    url = 'http://localhost:8000/auth-token/'
    data = {"username": username, "password": password}
    req = requests.post(url, json=data)

    if req.status_code == 200:
        token = req.json().get("token")
        token_cache[user_id] = {"token": token, "username": username, "password": password}
        return True, token
    return False, None

def save_telegram_id(token, telegram_id):
    url = "http://localhost:8000/auth/set-telegram-id/"
    headers = {"Authorization": f"Token {token}"}
    data = {"telegram_id": telegram_id}
    response = requests.post(url, json=data, headers=headers)
    if response.status_code == 200:
        print("Telegram ID saved successfully!")
    else:
        print("Failed to save Telegram ID:", response.json())

# End Login #

# Ticket & Logout #

async def handler_main(update, context):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    
    if update.message.text == 'Ticket':
        await context.bot.send_message(chat_id, 'Ticket Select!')
    elif update.message.text == 'Logout':
        await context.bot.send_message(chat_id, 'you logout!')
# End Ticket & Logout #

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text('cancelled!')
    return ConversationHandler.END

def main():
    application = ApplicationBuilder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            ACCOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, account)],
            USERNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, login_username)],
            PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, login_password)],
            MAIN_HANDLER: [MessageHandler(filters.TEXT & ~filters.COMMAND, handler_main)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
        )
    
    application.add_handler(conv_handler)
    application.run_polling()

if __name__ == '__main__':
    main()
    