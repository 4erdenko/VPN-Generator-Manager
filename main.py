import asyncio
import logging
import sys

import coloredlogs
from aiogram import Bot, Dispatcher

from config import BOT_API
from telegram.handlers import main_handler


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
        stream=sys.stdout,
    )
    coloredlogs.install(
        level='INFO',
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        isatty=True,
        stream=sys.stdout,
    )
    bot = Bot(token=BOT_API, parse_mode='HTML')
    dp = Dispatcher()

    dp.include_router(main_handler.router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
