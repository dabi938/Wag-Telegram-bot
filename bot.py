import time
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackContext, filters

# Replace with your Bot Token
BOT_TOKEN = '7577327684:AAHBVsQWRg5S54HdYWSZ5fsqTCOtfRAfby8'

# Replace with the hardcoded Chat ID of the bot owner
OWNER_CHAT_ID = 6742597078  # Replace with the actual Chat ID

# Replace with the username of the bot owner
OWNER_USERNAME = '@phinex938'

# To track sent messages and avoid duplication
sent_messages = set()

# Start command handler
async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text("Hi! I'll forward Your message or any type of file to Phinex.")

# Message handler
async def forward_message(update: Update, context: CallbackContext) -> None:
    user_message = update.message.text
    user_info = f"Message from @{update.message.chat.username if update.message.chat.username else f'ID: {update.message.chat.id}'}:\n\n"

    # Prevent duplicate message forwarding
    if user_message in sent_messages:
        return  # Skip if the message has already been sent

    # Mark this message as sent
    sent_messages.add(user_message)

    # Use hardcoded OWNER_CHAT_ID
    owner_chat_id = OWNER_CHAT_ID
    try:
        # Send the message to the owner
        await context.bot.send_message(chat_id=owner_chat_id, text=user_info + user_message)

        # Notify the user
        await update.message.reply_text("Your message has been sent!")
    except Exception as e:
        print(f"Error forwarding message: {e}")
        await update.message.reply_text("Failed to send the message. Please try again later.")

# File handler
async def forward_file(update: Update, context: CallbackContext) -> None:
    file = None

    if update.message.photo:
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

    # Use hardcoded OWNER_CHAT_ID
    owner_chat_id = OWNER_CHAT_ID
    try:
        # Forward the file to the owner based on its type
        if update.message.photo:
            await context.bot.send_photo(chat_id=owner_chat_id, photo=file_id)
        elif update.message.video:
            await context.bot.send_video(chat_id=owner_chat_id, video=file_id)
        else:
            await context.bot.send_document(chat_id=owner_chat_id, document=file_id)

        # Notify the user
        await update.message.reply_text("Your file has been sent!")
    except Exception as e:
        print(f"Error forwarding file: {e}")
        await update.message.reply_text("Failed to send the file. Please try again later.")

# Keep-alive task
async def keep_bot_active(application: Application):
    while True:
        try:
            # Send a dummy message to the bot owner
            await application.bot.send_message(chat_id=OWNER_CHAT_ID, text="Bot is alive and active.")
            print("Sent a keep-alive message.")
        except Exception as e:
            print(f"Error in keep-alive task: {e}")
        await asyncio.sleep(1200)  # Wait for 20 minutes (adjust as needed)

# Main function with restart mechanism
def main():
    try:
        # Create the application
        application = Application.builder().token(BOT_TOKEN).build()

        # Add handlers
        application.add_handler(CommandHandler("start", start))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, forward_message))
        application.add_handler(MessageHandler(filters.ALL & ~filters.TEXT, forward_file))

        # Schedule the keep-alive task
        application.job_queue.run_repeating(
            lambda context: asyncio.create_task(keep_bot_active(application)),
            interval=1200,  # 20 minutes
            first=0
        )

        # Start the bot
        print("Bot is running...")
        application.run_polling()
    except Exception as e:
        print(f"Bot encountered an error: {e}")
        print("Restarting bot...")
        time.sleep(5)  # Wait for a while before restarting the bot to prevent rapid restarts
        main()  # Restart the bot

if __name__ == "__main__":
    main()
