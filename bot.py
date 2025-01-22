import time
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackContext, filters

# Replace with your Bot Token
BOT_TOKEN = '7577327684:AAHBVsQWRg5S54HdYWSZ5fsqTCOtfRAfby8'

# Replace with the hardcoded Chat ID of the bot owner (once resolved)
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

    # Use hardcoded OWNER_CHAT_ID, fallback to dynamic username resolution if needed
    owner_chat_id = OWNER_CHAT_ID or await get_chat_id_by_username(context, OWNER_USERNAME)
    if not owner_chat_id:
        await update.message.reply_text("Sorry, I couldn't find the owner's chat ID.")
        return

    # Forward the file to the owner based on its type
    if update.message.photo:
        await context.bot.send_photo(chat_id=owner_chat_id, photo=file_id)
    elif update.message.video:
        await context.bot.send_video(chat_id=owner_chat_id, video=file_id)
    else:
        await context.bot.send_document(chat_id=owner_chat_id, document=file_id)

    # Notify the user
    await update.message.reply_text("Your file has been sent!")

# Function to resolve username to chat_id
async def get_chat_id_by_username(context: CallbackContext, username: str) -> int:
    try:
        user = await context.bot.get_chat(username)
        return user.id
    except Exception as e:
        print(f"Error resolving username to chat_id: {e}")
        return None

# Main function with restart mechanism
def main():
    while True:  # Start an infinite loop for restart handling
        try:
            # Create the application
            application = Application.builder().token(BOT_TOKEN).build()

            # Add handlers
            application.add_handler(CommandHandler("start", start))
            application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, forward_message))
            application.add_handler(MessageHandler(filters.ALL & ~filters.TEXT, forward_file))

            # Start the bot
            print("Bot is running...")
            application.run_polling()

        except Exception as e:
            print(f"Bot encountered an error: {e}")
            print("Restarting bot...")
            time.sleep(5)  # Wait for a while before restarting the bot to prevent rapid restarts

if __name__ == "__main__":
    main()
