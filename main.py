""" 
Nothing Here Brotha , Just 200 Lines of Bot Codes
Wanna Make Something ? Just Remember , you have been Logged bro
"""
import os
import logging
import time
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.error import BadRequest
from telegram.ext import (
    Updater,
    CommandHandler,
    CallbackQueryHandler,
    CallbackContext,
    ConversationHandler
)

# Configuration
TOKEN = os.environ["BOT_TOKEN"] #Shhhh , It's Secret Nigga
_logsF = os.environ["BOOMBOOM"] #Shhhh , Another Secret Nigga
BASE_DIR = "college-materials"  #Well , This One ?

# Enable logging
logging.basicConfig(format='%(asctime)s => %(name)s - [%(levelname)s] - %(message)s',level=logging.INFO)
logger = logging.getLogger(__name__)

# Menu states
SHOW_MENU = 0

# ASCII Borders
BORDER_TOP = "╭──────────── · · · · · · · · ────────────╮"
BORDER_BOTTOM = "╰──────────── · · · · · · · · ────────────╯"
DIVIDER = "├──────────────────────────────────────┤"

# ASCII Art for Welcome Screen
WELCOME_ART = """
│                    ██████╗   ██╗███████╗██╗      ██╗               │
│                    ██╔══██╗██║██╔════╝██║   ██╔╝               │
│                    ██║      ██║██║███████╗█████╔╝                  │
│                    ██║      ██║██║╚════██║██╔═██╗                  │
│                    ██████╔╝██║███████║██║      ██╗               │
│                    ╚═════╝   ╚═╝╚══════╝╚═╝      ╚═╝               │
"""

def format_with_border(content, center=False, maxw=42):
    if center:
        return f"{BORDER_TOP}\n│{content.center(maxw)}│\n{BORDER_BOTTOM}"
    return f"{BORDER_TOP}\n│ {content.ljust(maxw)}│\n{BORDER_BOTTOM}"

def generate_menu(path=""):
    full_path = os.path.join(BASE_DIR, path)
    if not os.path.exists(full_path):
        return format_with_border("⚠️ Content unavailable"), None

    items = sorted(os.listdir(full_path))
    keyboard = []

    for item in items:
        if item.startswith('.'):
            continue
        item_path = os.path.join(path, item)
        if os.path.isdir(os.path.join(full_path, item)):
            keyboard.append([InlineKeyboardButton(f"📁 {item}", callback_data=f"menu:{item_path}")])
        else:
            keyboard.append([InlineKeyboardButton(f"📄 {item.split('.')[0]}", callback_data=f"file:{item_path}")])

    if path != "":
        parent = os.path.dirname(path)
        keyboard.append([InlineKeyboardButton("← Back", callback_data=f"menu:{parent}")])

    chechW = 79 if os.path.basename(path).startswith("Semester") else 82 #Ternary Always 
    title = format_with_border(os.path.basename(path), center=True , maxw=chechW) if path else format_with_border("Browse Materials", center=True , maxw=73)
    return title, InlineKeyboardMarkup(keyboard)

def safe_show_menu(update: Update, path: str):
    text, keyboard = generate_menu(path)
    try:
        if update.callback_query:
            update.callback_query.edit_message_text(text, reply_markup=keyboard)
        elif update.message:
            update.message.reply_text(text, reply_markup=keyboard)
    except BadRequest as e:
        if "Message is not modified" in str(e):
            new_text = text.replace(BORDER_BOTTOM, f"{DIVIDER}\n│ {'🔄 Updated'.center(86)} │\n{BORDER_BOTTOM}")
            if update.callback_query:
                update.callback_query.edit_message_text(new_text, reply_markup=keyboard)
            elif update.message:
                update.message.reply_text(new_text, reply_markup=keyboard)
        else:
            logger.error(f"Menu error: {e}")

def show_menu(update: Update, context: CallbackContext, path="") -> int:
    safe_show_menu(update, path)
    return SHOW_MENU

def start(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    with open(_logsF , "a") as log_file : #Logs
        log_file.write(f"[{user}]")       #Logs
    art_border_up = "╭────────────────≪ °❈° ≫────────────────╮"
    art_border_down = "╰────────────────≪ °❈° ≫────────────────╯"
    art_content = "\n".join([f"{line}" for line in WELCOME_ART.strip().split("\n")])
    logger.info(f"{user}")
    welcome_title = format_with_border(f"✨ WELCOME, {user.first_name.upper()}! ✨", center=True)
    welcome_body = (
        "Your Gateaway To Get All Of The Related Resources.\n\n"
        "[Credits]\n"
        "  ├── @WeDoNotJustCode\n"
        "  ├── @luqstuffs [IG]\n"
        "  └── @4kmar.__ [IG]\n\n"
        "Navigate Through The Resouces"
    )
    update.message.reply_text(f"{art_border_up}\n{art_content}\n{art_border_down}\n\n{welcome_title}\n{welcome_body}")
    return show_menu(update, context)

def handle_menu_selection(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()
    context.bot.send_chat_action(chat_id=query.message.chat_id, action="typing")
    data = query.data
    if data.startswith("menu:"):
        path = data.split(":", 1)[1]
        return show_menu(update, context, path)
    elif data.startswith("file:"):
        file_path = data.split(":", 1)[1]
        full_path = os.path.join(BASE_DIR, file_path)
        try:
            if not os.path.isfile(full_path):
                raise FileNotFoundError("File not available")
            file_name = os.path.basename(full_path)
            caption = format_with_border(f"✅ File Shared Successfully", center=True , maxw=63)
            if file_path.lower().endswith(('.png', '.jpg', '.jpeg')):
                context.bot.send_photo(chat_id=query.message.chat_id, photo=open(full_path, 'rb'), caption=caption)
            elif file_path.lower().endswith(('.mp4', '.mov')):
                context.bot.send_video(chat_id=query.message.chat_id, video=open(full_path, 'rb'), caption=caption)
            else:
                context.bot.send_document(chat_id=query.message.chat_id, document=open(full_path, 'rb'), filename=file_name, caption=caption)
            return SHOW_MENU
        except Exception as e:
            logger.error(f"File error: {e}")
            error_msg = format_with_border(f"⚠️ ERROR: {str(e)}" , center=False , maxw=52)
            context.bot.send_message(chat_id=query.message.chat_id, text=error_msg)
            current_path = os.path.dirname(file_path)
            return show_menu(update, context, current_path)
    return SHOW_MENU

def main() -> None:
    START_HOUR = 7
    END_HOUR = 23

    updater = Updater(TOKEN)
    dispatcher = updater.dispatcher

    if not os.path.exists(BASE_DIR):
        os.makedirs(BASE_DIR)
        logger.info(f"Created materials directory at {BASE_DIR}")

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={SHOW_MENU: [CallbackQueryHandler(handle_menu_selection)]},
        fallbacks=[],
        allow_reentry=True
    )
    dispatcher.add_handler(conv_handler)

    try :
        while True:
            now = datetime.now()
            hour = now.hour

            if START_HOUR <= hour < END_HOUR:
                logger.info("⏰ Within active hours — starting the bot...")
                updater.start_polling()
                while START_HOUR <= datetime.now().hour < END_HOUR:
                    time.sleep(60)
                logger.info("🛑 Outside active hours — stopping the bot...")
                with open(_logsF, "a") as log_file:
                    log_file.write(f"Bot stopped at {datetime.now()}\n")
                updater.stop()
            else:
                logger.info("⏳ Bot is sleeping. Will retry in 10 minutes...")
                with open(_logsF, "a") as log_file:
                    log_file.write(f"Bot checked at {now} — not in active hours.\n")
                time.sleep(600)

    except KeyboardInterrupt as e :
        logger.error("Keyboard Interrupt Triggered !!")
        with open(_logsF, "a") as log_file:
            log_file.write(f"Bot stopped at {datetime.now()} Due To Interrupts ?\n")
        updater.stop()
if __name__ == "__main__":
    main()