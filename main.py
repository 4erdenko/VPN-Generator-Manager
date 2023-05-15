from aiogram import executor
from telegram.bot import dp
import logging




if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    executor.start_polling(dp, skip_updates=True)