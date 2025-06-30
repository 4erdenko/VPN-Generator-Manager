import asyncio
import logging
import sys

import coloredlogs
from aiogram import Bot, Dispatcher

from config import BOT_API, check_credentials
from telegram.handlers import main_handler
from telegram.keyboards.main_menu import set_main_menu


async def main():
    """Main function to start the bot."""
    try:
        # Check credentials before starting
        check_credentials()
        
        # Setup logging
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
        
        logger = logging.getLogger(__name__)
        logger.info("Starting VPN Bot Manager...")
        
        # Initialize bot and dispatcher
        bot = Bot(token=BOT_API, parse_mode='HTML')
        dp = Dispatcher()
        
        # Setup menu and handlers
        await set_main_menu(bot)
        dp.include_router(main_handler.router)

        # Start polling
        await bot.delete_webhook(drop_pending_updates=True)
        logger.info("Bot started successfully")
        await dp.start_polling(bot)
        
    except ValueError as e:
        logging.error(f"Configuration error: {e}")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Failed to start bot: {e}")
        sys.exit(1)


if __name__ == '__main__':
    asyncio.run(main())
