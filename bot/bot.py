import sys
import os
import logging
import requests
import json
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "website.settings")

import django
django.setup()

from accounts.models import CustomUserModel
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler, MessageHandler, ConversationHandler, filters, Application,CallbackContext

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()
TOKEN = os.getenv('TOKEN')
ADMIN_ID = os.getenv('ADMIN')

(ACCOUNT, LOGIN, SINGUP, USERNAME, PASSWORD, MAIN_HANDLER, TICKET, TICKET_COMPANY,TICKET_COMMENT, TICKET_CREATE, LOGOUT,
REGISTER_FIRSTNAME, REGISTER_LASTNAME, REGISTER_EMAIL, REGISTER_PASSWORD, REGISTER_USERNAME, REGISTER_CREATE,
SEND_ANSWER, ID_TICKET, SUBJECT, MESSAGE, ADMIN_HANDLER) = range(22)
token_cache = {}

async def start(update, context):
    
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    fullname = update.message.from_user.full_name 
    
    if not user_id in token_cache:
        await update.message.reply_text(f"Hello {fullname}, welcome to the ticket robot")
        keyboard = [['Login'], ['Signup']]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await context.bot.send_message(chat_id=chat_id,
                                    text='Please choose:',
                                    reply_markup=reply_markup)
        print("Returning ACCOUNT")
        return ACCOUNT
    else:
        profile = get_user_profile(user_id)
        if not profile:
            return False
        name = profile['first_name']
        await update.message.reply_text(f'{name} You are currently logged in')
        print("Returning MAIN_HANDLER")
        return MAIN_HANDLER
# Account Handler #

async def account(update, context):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id

    keyboard = [['Back']]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    if update.message.text == 'Login':
        await context.bot.send_message(chat_id, 'Your username:', reply_markup=reply_markup)
        return USERNAME

    elif update.message.text == 'Signup':
        await update.message.reply_text("Your FirstName:", reply_markup=reply_markup)
        return REGISTER_FIRSTNAME
    else:
        await context.bot.send_message(chat_id, 'Please select a valid option')

# End Account Handler #

# Login #
async def login_username(update, context):
    if update.message.text == 'Back':
        return await start(update, context)
    
    context.user_data["username"] = update.message.text
    await update.message.reply_text("Your password:")
    
    return PASSWORD

async def login_password(update, context):

    if update.message.text == 'Back':
        return await start(update, context)

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

async def handler_ticket_but(update, context):
    chat_id = update.effective_chat.id
    await context.bot.send_message(chat_id, text='Choose from the desired options')
    return MAIN_HANDLER

async def main_menu_handler(update, context):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id

    keyboard = [['Back']]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    
    if text == 'Ticket':
        await context.bot.send_message(chat_id=chat_id, text="Great — let's register your ticket", reply_markup=reply_markup)
        await context.bot.send_message(chat_id=chat_id, text="Send your company name or type 'skip'")
        return TICKET
    elif text == 'Logout':
        await logout_handler(update, context)
        return await start(update, context)
    elif text == 'Back':
        await context.bot.send_message(chat_id=chat_id, text='Back to main menu.')
        return MAIN_HANDLER
    elif text == 'Answer':
        await context.bot.send_message(chat_id=chat_id, text='Hi, Admin!')
        await context.bot.send_message(chat_id=chat_id, text='Send ticket ID:')
        return ID_TICKET
    else:
        await context.bot.send_message(chat_id=chat_id, text='Please select a valid option!')
        return MAIN_HANDLER
        


async def ticket_company(update, context):

    chat_id = update.effective_chat.id
    
    if update.message.text == 'Back':
        keyboard = [['Ticket'], ['Logout']]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text("Please choose:", reply_markup=reply_markup)
        return MAIN_HANDLER

    company_name = update.message.text
    
    if company_name.lower() == 'skip':
        company_name = "No company provided"
    
    keyboard = [['Back']]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    context.user_data["company_name"] = company_name
    await context.bot.send_message(chat_id, 'Now please send your comment:', reply_markup=reply_markup)
    return TICKET_COMMENT

async def ticket_comment(update, context):
    chat_id = update.effective_chat.id
    
    if update.message.text == 'Back':
        keyboard = [['Ticket'], ['Logout']]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text("Please choose:", reply_markup=reply_markup)
        return MAIN_HANDLER

    comment = update.message.text


    if len(comment) < 15:
        await context.bot.send_message(chat_id, 'Your message is shorter than 15 words. Try again')
        keyboard = [['Ticket'], ['Logout']]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text("Please choose:", reply_markup=reply_markup)
        return MAIN_HANDLER
    else:
        context.user_data["comment"] = comment
        
        await create_ticket(update, context)
        return TICKET_CREATE

def get_user_profile(user_id):
    token = token_cache[user_id]["token"]
    url = "http://127.0.0.1:8000/auth/profile/"
    headers = {"Authorization": f"Token {token}"}
    req = requests.get(url, headers=headers)

    if req.status_code == 200:
        return req.json()
    return None

async def create_ticket(update, context):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id  
    company_name = context.user_data.get("company_name", "N/A")
    comment = context.user_data.get("comment", "No comment")
    
    try:
        success = await send_ticket_request(user_id, update, context, company_name, comment)
        if success:
            await context.bot.send_message(chat_id, 'Ticket created!')
            keyboard = [['Ticket'], ['Logout']]
            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
            await update.message.reply_text("Please choose:", reply_markup=reply_markup)
            return MAIN_HANDLER
        else:
            await context.bot.send_message(chat_id, 'Could not create ticket, try again later.')
            keyboard = [['Ticket'], ['Logout']]
            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
            await update.message.reply_text("Please choose:", reply_markup=reply_markup)            
            return MAIN_HANDLER
    except Exception as e:
        await context.bot.send_message(chat_id, f'Try again later. Error: {e}')
        keyboard = [['Ticket'], ['Logout']]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text("Please choose:", reply_markup=reply_markup)
        return MAIN_HANDLER


async def send_ticket_request(user_id, update, context, company_name, comments):
    token = token_cache[user_id]["token"]
    url = "http://localhost:8000/ticket/tickets/"
    headers = {"Authorization": f"Token {token}"}

    profile = get_user_profile(user_id)
    if not profile:
        return False

    data = {
        "user": profile["id"],
        "name": profile["first_name"],
        "lastname": profile["last_name"],
        "email": profile["email"],
        "Company_name": company_name,
        "comments": comments
    }

    req = requests.post(url, headers=headers, json=data)
    data = json.loads(req.text)
    await context.bot.send_message(
    ADMIN_ID,
    f"🎫 *New Ticket Request*\n\n"
    f"👤 *Name:* {data['name']} {data['lastname']}\n"
    f"📧 *Email:* {data['email']}\n"
    f"🏢 *Company:* {data['Company_name']}\n"
    f"📅 *Date:* {data['date']}\n"
    f"💬 *Comments:* {data['comments']}\n\n"
    f"🆔 *User ID:* {data['user']}\n"
    f"🆔 *Ticket ID:* {data['id']}"
    
    f"🆔 *User ID:* {user_id}",
    parse_mode='Markdown'
    )
    return req.status_code == 201

async def logout(user_id):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    token_cache.pop(user_id, None)
    await context.bot.send_message(chat_id=chat_id, text='You have been logged out.')
    return ACCOUNT
# End Ticket & Logout #

# Register #
async def register_firstname(update, context):
    if update.message.text == 'Back':
        return await start(update, context)
    
    context.user_data["first_name"] = update.message.text
    await update.message.reply_text("Your LastName:")
    
    return REGISTER_LASTNAME


async def register_lastname(update, context):
    if update.message.text == 'Back':
        return await start(update, context)

    context.user_data["last_name"] = update.message.text
    await update.message.reply_text("Your Email:")
    return REGISTER_EMAIL

async def register_email(update, context):
    if update.message.text == 'Back':
        return await start(update, context)

    context.user_data["email"] = update.message.text
    await update.message.reply_text("Your Username:")
    return REGISTER_USERNAME

async def register_username(update, context):
    if update.message.text == 'Back':
        return await start(update, context)

    context.user_data["username"] = update.message.text
    await update.message.reply_text("Your Password:")
    return REGISTER_PASSWORD

async def register_password(update, context):
    if update.message.text == 'Back':
        return await start(update, context)

    chat_id = update.effective_chat.id
    context.user_data["password"] = update.message.text
    await update.message.reply_text("Please wait, creating your account...")

    first_name = context.user_data["first_name"]
    last_name = context.user_data["last_name"]
    email = context.user_data["email"]
    username = context.user_data["username"]
    password = context.user_data["password"]
    
    try:
        success = await register_create(first_name, last_name, email, username, password)
        if success:
            await update.message.delete()
            await context.bot.send_message(chat_id, "Your account has been created successfully! \n now login your account!")
            keyboard = [['Login'], ['Signup']]
            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
            await context.bot.send_message(chat_id=chat_id,
                                    text='Please choose:',
                                    reply_markup=reply_markup)
            return ACCOUNT 
        else:
            await context.bot.send_message(chat_id, "I could not create the account, there is a problem, try again")
            keyboard = [['Login'], ['Signup']]
            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
            await context.bot.send_message(chat_id=chat_id,
                                    text='Please choose:',
                                    reply_markup=reply_markup)
            return ACCOUNT 
        return ACCOUNT
    except Exception as e:
        await context.bot.send_message(chat_id, f"Error: {e}")
        return ACCOUNT

async def register_create(first_name, last_name, email, username, password):

    url = "http://localhost:8000/auth/users/"

    data = {
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "username": username,
        "password": password
    }

    req = requests.post(url, json=data)
    return req.status_code == 201

# End Register #

# Answer Ticket #
# ANSWER_HANDLER, ID_TICKET, SUBJECT, MESSAGE
async def admin_handler(update, context):
    
    if update.message.text == 'Answer':
        await context.bot.send_message(chat_id, 'Hi, Admin!')
        await context.bot.send_message(chat_id, 'Send ticket ID:')
        return ID_TICKET
    elif update.message.text == 'Logout':
        await context.bot.send_message(chat_id, 'You have been logged out!')
        await logout(user_id)
        return await start(update, context)

    elif update.message.text == 'Back':
        await context.bot.send_message(chat_id, 'Back to main menu!')
        return MAIN_HANDLER
    else:
        await context.bot.send_message(chat_id, 'Please select a valid option!')   

async def id_ticket(update, context):

    chat_id = update.effective_chat.id

    if update.message.text == 'Back':
        keyboard = [['Answer'], ['Logout']]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text("Please choose:", reply_markup=reply_markup)
        return MAIN_HANDLER

    context.user_data["id_ticket_number"] = update.message.text
    await context.bot.send_message(chat_id, 'Now send subject:')
    return SUBJECT

async def subjcet(update, context):

    chat_id = update.effective_chat.id

    if update.message.text == 'Back':
        keyboard = [['Answer'], ['Logout']]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text("Please choose:", reply_markup=reply_markup)
        return MAIN_HANDLER

    context.user_data["subject_text"] = update.message.text
    await context.bot.send_message(chat_id, 'now send your message')
    return MESSAGE

async def message(update, context):
    
    chat_id = update.effective_chat.id

    if update.message.text == 'Back':
        keyboard = [['Answer'], ['Logout']]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text("Please choose:", reply_markup=reply_markup)
        return MAIN_HANDLER

    context.user_data["message_text"] = update.message.text
    await context.bot.send_message(chat_id, 'Send Telegram ID of the user to receive the answer:')
    return SEND_ANSWER

async def send_answer(update, context):

    user_id = update.effective_user.id
    id_tic = context.user_data["id_ticket_number"]
    subject_answer = context.user_data["subject_text"]
    message_answer = context.user_data["message_text"]
    id_number_tel = update.message.text

    token = token_cache[user_id]["token"]
    url = "http://localhost:8000/ticket/answers/"
    headers = {"Authorization": f"Token {token}"}

    data = {
        "ticket": id_tic,
        "subject": subject_answer,
        "message_text": message_answer,
    }

    req = requests.post(url, headers=headers, json=data)
    if req.status_code == 201:
        await context.bot.send_message(id_number_tel, text=f'Admin Answer:{message_answer}')
        keyboard = [['Answer'], ['Logout']]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text("Please choose:", reply_markup=reply_markup)
        return ACCOUNT
    else:
        await context.bot.send_message(ADMIN_ID, 'Erorr!')
        keyboard = [['Answer'], ['Logout']]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text("Please choose:", reply_markup=reply_markup)
        return ACCOUNT

# End Answer Ticket #
async def cancel(update, context):
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
            MAIN_HANDLER: [MessageHandler(filters.TEXT & ~filters.COMMAND, main_menu_handler)],
            TICKET: [MessageHandler(filters.TEXT & ~filters.COMMAND, ticket_company)],
            TICKET_COMPANY: [MessageHandler(filters.TEXT & ~filters.COMMAND, ticket_company)],
            TICKET_COMMENT: [MessageHandler(filters.TEXT & ~filters.COMMAND, ticket_comment)],
            TICKET_CREATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, create_ticket)],
            LOGOUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, logout)],

            REGISTER_FIRSTNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, register_firstname)],
            REGISTER_LASTNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, register_lastname)],
            REGISTER_EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, register_email)],
            REGISTER_USERNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, register_username)],
            REGISTER_PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, register_password)],
            REGISTER_CREATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, register_create)],

            ID_TICKET: [MessageHandler(filters.TEXT & ~filters.COMMAND, id_ticket)],
            SUBJECT: [MessageHandler(filters.TEXT & ~filters.COMMAND, subjcet)],
            MESSAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, message)],
            SEND_ANSWER: [MessageHandler(filters.TEXT & ~filters.COMMAND, send_answer)],
            ADMIN_HANDLER: [MessageHandler(filters.TEXT & ~filters.COMMAND, admin_handler)],
            
        },
        fallbacks=[CommandHandler("cancel", cancel),CommandHandler("start", start)],
        )
    
    application.add_handler(conv_handler)
    application.run_polling()

if __name__ == '__main__':
    main()
    