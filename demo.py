from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackContext, filters
import logging
import os

# Replace with your Bot Token
BOT_TOKEN = '7577327684:AAHBVsQWRg5S54HdYWSZ5fsqTCOtfRAfby8'

# Replace with the hardcoded Chat ID of the bot owner
OWNER_CHAT_ID = 6742597078  # Replace with the actual Chat ID
OWNER_USERNAME = '@phinex938'

# Flask app for webhook
app = Flask(__name__)

# Global variables for bot application and sent messages
application = None
sent_messages = set()

# Logging setup
logging.basicConfig(level=logging.INFO)

# Start command handler
async def start(update: Update, context: CallbackContext) -> None:
    if update.message.chat_id == OWNER_CHAT_ID:
        return
    await update.message.reply_text("Hi! Welcome. I'll forward your message or any type of file to Phinex.")

# Message handler
async def forward_message(update: Update, context: CallbackContext) -> None:
    user_message = update.message.text
    user_info = f"Message from @{update.message.chat.username if update.message.chat.username else f'ID: {update.message.chat.id}'}:\n\n"
    if user_message in sent_messages:
        return
    sent_messages.add(user_message)
    await context.bot.send_message(chat_id=OWNER_CHAT_ID, text=user_info + user_message)
    await update.message.reply_text("Your message has been sent!")

# File handler
async def forward_file(update: Update, context: CallbackContext) -> None:
    file = update.message.document or update.message.photo or update.message.video or update.message.audio or update.message.voice
    if not file:
        await update.message.reply_text("Unsupported file type.")
        return
    user_info = f"From @{update.message.chat.username if update.message.chat.username else f'ID: {update.message.chat.id}'}:\n"
    await context.bot.send_document(chat_id=OWNER_CHAT_ID, document=file.file_id, caption=user_info)
    await update.message.reply_text("Your file has been sent!")

# Webhook route
@app.route('/webhook', methods=['POST'])
def webhook():
    json_str = request.get_data(as_text=True)
    update = Update.de_json(json_str, application.bot)
    application.process_update(update)
    return '', 200

# Periodic message sender
async def send_periodic_message(context: CallbackContext) -> None:
    try:
        await context.bot.send_message(
            chat_id=OWNER_CHAT_ID, 
            text="Periodic message to prevent bot inactivity.", 
            disable_notification=True  # Sends the message silently
        )
    except Exception as e:
        logging.error(f"Error sending periodic message: {e}")

# Application setup
def setup_application():
    global application
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, forward_message))
    application.add_handler(MessageHandler(filters.ALL & ~filters.TEXT, forward_file))
    application.job_queue.run_repeating(send_periodic_message, interval=300, first=0)  # Every 5 minutes
    return application

if __name__ == '__main__':
    # Initialize the bot application
    app_port = int(os.environ.get('PORT', 5000))
    webhook_url = "https://wag-telegram-bot.onrender.com/webhook"  # Replace with your deployed domain

    application = setup_application()

    # Set the webhook
    application.bot.set_webhook(webhook_url)

    # Run the Flask app
    app.run(host='0.0.0.0', port=app_port)
