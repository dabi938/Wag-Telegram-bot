import os
from fastapi import FastAPI, Request
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

# Create the FastAPI app
app = FastAPI()

# Telegram bot application
application = Application.builder().token(BOT_TOKEN).build()

# Add bot handlers
async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text("Hi! I'll forward your message or any type of file to Phinex.")

async def forward_message(update: Update, context: CallbackContext) -> None:
    user_message = update.message.text
    user_info = f"Message from @{update.message.chat.username if update.message.chat.username else f'ID: {update.message.chat.id}'}:\n\n"

    if user_message in sent_messages:
        return  # Skip duplicate messages

    sent_messages.add(user_message)

    if not OWNER_CHAT_ID:
        await update.message.reply_text("Sorry, I couldn't find the owner's chat ID.")
        return

    await context.bot.send_message(chat_id=OWNER_CHAT_ID, text=user_info + user_message)
    await update.message.reply_text("Your message has been sent!")

application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, forward_message))

@app.post("/webhook")
async def telegram_webhook(request: Request):
    update = Update.de_json(await request.json(), application.bot)
    await application.update_queue.put(update)
    return {"status": "ok"}

@app.on_event("startup")
async def on_startup():
    webhook_url = f" https://wag-telegram-5iyohyk4o-dabis-projects-f3c1438b.vercel.app "  # Replace with your Vercel deployment URL
    await application.bot.set_webhook(url=webhook_url)

