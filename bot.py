import time
import logging
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackContext, filters
from telegram.error import TimedOut, NetworkError, RetryAfter, BadRequest

# Replace with your Bot Token
BOT_TOKEN = '7577327684:AAHBVsQWRg5S54HdYWSZ5fsqTCOtfRAfby8'

# Replace with the hardcoded Chat ID of the bot owner
OWNER_CHAT_ID = 6742597078

# Track sent messages to avoid duplication
sent_messages = set()

# Set up logging
logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)

# Start command
async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text("Hi! I'll forward your message or any type of file to Phinex.")

# Message handler (Handles text messages)
async def forward_message(update: Update, context: CallbackContext) -> None:
    user_message = update.message.text
    user_username = update.message.chat.username
    user_identifier = f"@{user_username}" if user_username else f"ID: {update.message.chat.id}"

    if user_message in sent_messages:
        return
    sent_messages.add(user_message)

    try:
        logging.info(f"Forwarding message: {user_message} from {user_identifier}")
        await context.bot.send_message(chat_id=OWNER_CHAT_ID, text=f"Message from {user_identifier}: \n\n{user_message}")
        await update.message.reply_text("Your message has been forwarded.")
    except Exception as e:
        logging.error(f"Error forwarding message: {e}")
        await update.message.reply_text("There was an issue forwarding your message. Please try again.")

# File handler (Handles all file types including documents, photos, etc.)
async def forward_file(update: Update, context: CallbackContext) -> None:
    user_username = update.message.chat.username
    user_identifier = f"@{user_username}" if user_username else f"ID: {update.message.chat.id}"
    
    try:
        logging.info(f"Forwarding file from {user_identifier}")
        if update.message.document:
            await context.bot.send_document(chat_id=OWNER_CHAT_ID, document=update.message.document.file_id)
            await context.bot.send_message(chat_id=OWNER_CHAT_ID, text=f"Document from {user_identifier}")
            await update.message.reply_text("Your document has been forwarded.")
        elif update.message.photo:
            photo = update.message.photo[-1]
            await context.bot.send_photo(chat_id=OWNER_CHAT_ID, photo=photo.file_id)
            await context.bot.send_message(chat_id=OWNER_CHAT_ID, text=f"Photo from {user_identifier}")
            await update.message.reply_text("Your photo has been forwarded.")
        elif update.message.video:
            await context.bot.send_video(chat_id=OWNER_CHAT_ID, video=update.message.video.file_id)
            await context.bot.send_message(chat_id=OWNER_CHAT_ID, text=f"Video from {user_identifier}")
            await update.message.reply_text("Your video has been forwarded.")
        elif update.message.audio:
            await context.bot.send_audio(chat_id=OWNER_CHAT_ID, audio=update.message.audio.file_id)
            await context.bot.send_message(chat_id=OWNER_CHAT_ID, text=f"Audio from {user_identifier}")
            await update.message.reply_text("Your audio has been forwarded.")
        elif update.message.voice:
            await context.bot.send_voice(chat_id=OWNER_CHAT_ID, voice=update.message.voice.file_id)
            await context.bot.send_message(chat_id=OWNER_CHAT_ID, text=f"Voice message from {user_identifier}")
            await update.message.reply_text("Your voice message has been forwarded.")
        elif update.message.sticker:
            await context.bot.send_sticker(chat_id=OWNER_CHAT_ID, sticker=update.message.sticker.file_id)
            await context.bot.send_message(chat_id=OWNER_CHAT_ID, text=f"Sticker from {user_identifier}")
            await update.message.reply_text("Your sticker has been forwarded.")
        elif update.message.video_note:
            await context.bot.send_video_note(chat_id=OWNER_CHAT_ID, video_note=update.message.video_note.file_id)
            await context.bot.send_message(chat_id=OWNER_CHAT_ID, text=f"Video note from {user_identifier}")
            await update.message.reply_text("Your video note has been forwarded.")
        elif update.message.location:
            await context.bot.send_message(chat_id=OWNER_CHAT_ID, text=f"Location from {user_identifier}: {update.message.location.latitude}, {update.message.location.longitude}")
            await update.message.reply_text("Your location has been forwarded.")
        elif update.message.contact:
            contact = update.message.contact
            await context.bot.send_message(chat_id=OWNER_CHAT_ID, text=f"Contact from {user_identifier}: {contact.first_name} {contact.last_name}, {contact.phone_number}")
            await update.message.reply_text("Your contact info has been forwarded.")
        else:
            await update.message.reply_text("Unsupported file type.")
    
    except Exception as e:
        logging.error(f"Error forwarding file: {e}")
        await update.message.reply_text("There was an issue forwarding your file. Please try again.")

# Error handler
async def handle_error(update: object, context: CallbackContext) -> None:
    logging.error(f"Update {update} caused error {context.error}")
    await context.bot.send_message(chat_id=OWNER_CHAT_ID, text=f"Error: {context.error}")

# Restart bot function
async def restart_bot(application: Application):
    logging.info("Shutting down bot...")
    if application.running:
        await application.shutdown()
    await application.stop()
    logging.info("Bot shut down successfully.")

# Main function
def main():
    while True:
        try:
            application = Application.builder().token(BOT_TOKEN).build()

            application.add_handler(CommandHandler("start", start))
            application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, forward_message))
            application.add_handler(MessageHandler(filters.ALL & ~filters.TEXT, forward_file))

            application.add_error_handler(handle_error)

            logging.info("Bot is running...")
            application.run_polling(allowed_updates=Update.ALL_TYPES, timeout=300, poll_interval=10)

        except (TimedOut, NetworkError, RetryAfter, BadRequest) as e:
            logging.error(f"Bot encountered a network error or timeout: {e}. Restarting...")
            time.sleep(5)  # Delay before restarting
        except Exception as e:
            logging.error(f"Bot encountered an error: {e}. Restarting...")
            time.sleep(5)  # Delay before restarting

        finally:
            logging.info("Restarting bot...")
            time.sleep(5)  # Delay to avoid a rapid restart loop

if __name__ == "__main__":
    main()
