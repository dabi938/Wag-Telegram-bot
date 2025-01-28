# Use Python as the base image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy the bot script and install dependencies
COPY . /app

# Install required libraries
RUN pip install --no-cache-dir python-telegram-bot

# Command to run the bot
CMD ["python", "bot.py"]
