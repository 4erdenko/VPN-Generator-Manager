import logging
import sys

from aiogram import executor

# Imports the dispatcher from bot.py.
from telegram.bot import dp

if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
        stream=sys.stdout)

    # Starts the bot.
    executor.start_polling(dp, skip_updates=True)
