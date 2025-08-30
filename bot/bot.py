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

ACCOUNT, LOGIN, SINGUP, USERNAME, PASSWORD, MAIN_HANDLER, TICKET, TICKET_COMPANY,TICKET_COMMENT, TICKET_CREATE = range(10)
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
    tel_username = update.message.chat.username
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
        save_telegram_id(token, user_id, tel_username)
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

def save_telegram_id(token, telegram_id, tel_username):
    url = "http://localhost:8000/auth/set-telegram-id/"
    headers = {"Authorization": f"Token {token}"}
    data = {"telegram_id": telegram_id, "tel_username": tel_username}
    response = requests.post(url, json=data, headers=headers)

    if response.status_code == 200:
        print("Telegram ID saved successfully!")
    else:
        print("Failed to save Telegram ID:", response.text)



# End Login #

# Ticket & Logout #
def get_protected_data(user_id):
    if user_id not in token_cache:
        return "User not logged in"

    token = token_cache[user_id]["token"]
    url = "http://localhost:8000/auth/"
    headers = {"Authorization": f"Token {token}"}
    
    req = requests.get(url, headers=headers)
    if req.status_code == 200:
        return req.json()
    return req.text

async def handler_main(update, context):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    
    if update.message.text == 'Ticket':
        await context.bot.send_message(chat_id, "It's great, let's go to register the ticket")
        await context.bot.send_message(chat_id, "Send me your company name or send skip text")
        return TICKET
    elif update.message.text == 'Logout':
        await context.bot.send_message(chat_id, 'You have been logged out!')

async def ticket_company(update, context):
    chat_id = update.effective_chat.id
    company_name = update.message.text
    
    if company_name.lower() == 'skip':
        company_name = "No company provided"
    
    context.user_data["company_name"] = company_name
    await context.bot.send_message(chat_id, 'Now please send your comment:')
    return TICKET_COMMENT

async def ticket_comment(update, context):
    chat_id = update.effective_chat.id
    comment = update.message.text
    context.user_data["comment"] = comment
    
    await create_ticket(update, context)
    return TICKET_CREATE

async def create_ticket(update, context):
    chat_id = update.effective_chat.id
    company_name = context.user_data.get("company_name", "N/A")
    comment = context.user_data.get("comment", "No comment")
    
    # ticket_result = create_ticket_api(company_name, comment)
    
    await context.bot.send_message(chat_id, f'Ticket created!\nCompany: {company_name}\nComment: {comment}')
    
    context.user_data.pop("company_name", None)
    context.user_data.pop("comment", None)



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
            TICKET: [MessageHandler(filters.TEXT & ~filters.COMMAND, ticket_company)],
            TICKET_COMPANY: [MessageHandler(filters.TEXT & ~filters.COMMAND, ticket_company)],
            TICKET_COMMENT: [MessageHandler(filters.TEXT & ~filters.COMMAND, ticket_comment)],
            TICKET_CREATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, create_ticket)],

            
        },
        fallbacks=[CommandHandler('cancel', cancel)],
        )
    
    application.add_handler(conv_handler)
    application.run_polling()

if __name__ == '__main__':
    main()
    