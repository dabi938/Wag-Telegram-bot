import time
from telegram import Bot, Update
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackContext, filters
import asyncio
import logging
from flask import Flask, request

# Replace with your Bot Token
BOT_TOKEN = '7577327684:AAHBVsQWRg5S54HdYWSZ5fsqTCOtfRAfby8'

# Replace with the hardcoded Chat ID of the bot owner (once resolved)
OWNER_CHAT_ID = 6742597078  # Replace with the actual Chat ID

# Replace with the username of the bot owner
OWNER_USERNAME = '@phinex938'

# Initialize the bot and application
bot = Bot(token=BOT_TOKEN)
application = Application.builder().token(BOT_TOKEN).build()

# To track sent messages and avoid duplication
sent_messages = set()

# Flask app for webhook
app = Flask(__name__)

# Start command handler
async def start(update: Update, context: CallbackContext) -> None:
    if update.message.chat_id == OWNER_CHAT_ID:
        # Do not send the message to the owner
        return
    await update.message.reply_text("Hi! Welcome, I'll forward your message or any type of file to Phinex.")

# Message handler
async def forward_message(update: Update, context: CallbackContext) -> None:
    user_message = update.message.text
    user_info = f"Message from @{update.message.chat.username if update.message.chat.username else f'ID: {update.message.chat.id}'}:\n\n"

    # Prevent duplicate message forwarding
    if user_message in sent_messages:
        return  # Skip if the message has already been sent

    # Mark this message as sent
    sent_messages.add(user_message)

    # Use hardcoded OWNER_CHAT_ID, fallback to dynamic username resolution if needed
    owner_chat_id = OWNER_CHAT_ID or await get_chat_id_by_username(context, OWNER_USERNAME)
    if not owner_chat_id:
        await update.message.reply_text("Sorry, I couldn't find the owner's chat ID.")
        return

    # Send the message to the owner
    await context.bot.send_message(chat_id=owner_chat_id, text=user_info + user_message)

    # Notify the user
    await update.message.reply_text("Your message has been sent!")

# File handler
async def forward_file(update: Update, context: CallbackContext) -> None:
    # Check for different file types
    file = None

    if update.message.photo:
        # Get the highest resolution photo
        file = update.message.photo[-1]
    elif update.message.document:
        file = update.message.document
    elif update.message.audio:
        file = update.message.audio
    elif update.message.video:
        file = update.message.video
    elif update.message.voice:
        file = update.message.voice
    elif update.message.video_note:
        file = update.message.video_note

    if not file:
        await update.message.reply_text("Unsupported file type.")
        return

    file_id = file.file_id

    # Gather user information
    user_info = f"From @{update.message.chat.username if update.message.chat.username else f'ID: {update.message.chat.id}'}:\n"

    # Use hardcoded OWNER_CHAT_ID, fallback to dynamic username resolution if needed
    owner_chat_id = OWNER_CHAT_ID or await get_chat_id_by_username(context, OWNER_USERNAME)
    if not owner_chat_id:
        await update.message.reply_text("Sorry, I couldn't find the owner's chat ID.")
        return

    # Forward the file to the owner with user info as a caption
    if update.message.photo:
        await context.bot.send_photo(chat_id=owner_chat_id, photo=file_id, caption=user_info)
    elif update.message.video:
        await context.bot.send_video(chat_id=owner_chat_id, video=file_id, caption=user_info)
    elif update.message.audio:
        await context.bot.send_audio(chat_id=owner_chat_id, audio=file_id, caption=user_info)
    elif update.message.voice:
        await context.bot.send_voice(chat_id=owner_chat_id, voice=file_id, caption=user_info)
    elif update.message.document:
        await context.bot.send_document(chat_id=owner_chat_id, document=file_id, caption=user_info)
    elif update.message.video_note:
        await context.bot.send_video_note(chat_id=owner_chat_id, video_note=file_id)

    # Notify the user
    await update.message.reply_text("Your file has been sent!")

# Forwarded message handler
async def forward_forwarded_message(update: Update, context: CallbackContext) -> None:
    if update.message.forward_from:
        forwarded_from = update.message.forward_from.username or f"ID: {update.message.forward_from.id}"
        user_info = f"Forwarded message from @{forwarded_from}:\n\n"

        # Use hardcoded OWNER_CHAT_ID, fallback to dynamic username resolution if needed
        owner_chat_id = OWNER_CHAT_ID or await get_chat_id_by_username(context, OWNER_USERNAME)
        if not owner_chat_id:
            await update.message.reply_text("Sorry, I couldn't find the owner's chat ID.")
            return

        # Forward the message to the owner
        await context.bot.send_message(chat_id=owner_chat_id, text=user_info + update.message.text)

        # Notify the user
        await update.message.reply_text("Your forwarded message has been sent!")

# Function to resolve username to chat_id
async def get_chat_id_by_username(context: CallbackContext, username: str) -> int:
    try:
        user = await context.bot.get_chat(username)
        return user.id
    except Exception as e:
        print(f"Error resolving username to chat_id: {e}")
        return None

# Function to send periodic messages
async def send_periodic_message(context: CallbackContext) -> None:
    try:
        await context.bot.send_message(
            chat_id=OWNER_CHAT_ID, 
            text="....", 
            disable_notification=True  # To make the message silent
        )
    except Exception as e:
        print(f"Error sending periodic message: {e}")

# Webhook route to receive updates
@app.route('/webhook', methods=['POST'])
def webhook():
    json_str = request.get_data(as_text=True)
    update = Update.de_json(json_str, bot)
    application.process_update(update)
    return '', 200

# Main function with restart mechanism
def main():
    # Create the application
    application = Application.builder().token(BOT_TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, forward_message))
    application.add_handler(MessageHandler(filters.ALL & ~filters.TEXT, forward_file))
    application.add_handler(MessageHandler(filters.FORWARDED, forward_forwarded_message))

    # Schedule periodic messages
    application.job_queue.run_repeating(send_periodic_message, interval=420, first=0)

    # Set webhook URL
    webhook_url = 'https://wag-telegram-bot.onrender.com'
    application.bot.set_webhook(url=webhook_url)

    # Run the Flask app (This should be done in a separate thread if running alongside other services)
    app.run(host='0.0.0.0', port=5000)

if __name__ == "__main__":
    main()



