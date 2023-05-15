import os
from datetime import datetime, timedelta
from pytz import timezone
import aiogram
from aiogram.dispatcher.filters import Text

from api.vpn_generator import make_config, get_user, shorten_name
from config import BOT_API, CHAT_ID
from telegram.keyboards import main_keyboard

bot = aiogram.Bot(token=BOT_API)
dp = aiogram.Dispatcher(bot)


@dp.message_handler(commands=['start'])
async def start(message: aiogram.types.Message):
    if message.from_user.id != CHAT_ID:
        return
    await message.answer(
        'Hello, Mischievous Bednorz!', reply_markup=main_keyboard
    )


@dp.message_handler(Text(equals='🔐 Make config'))
async def get_config(message: aiogram.types.Message):
    filename = make_config()
    with open(filename, 'rb') as file:
        await message.answer_document(file, caption=filename)
    os.remove(filename)


@dp.message_handler(Text(equals='📝 Get users'))
async def get_users(message: aiogram.types.Message):
    user_list = get_user()
    result = []
    for user in user_list:
        last_visit = user.get('LastVisitHour')
        if last_visit is not None:
            last_visit = datetime.strptime(last_visit, '%Y-%m-%dT%H:%M:%S.%fZ')
            last_visit = last_visit.replace(tzinfo=timezone('UTC'))
            last_visit = last_visit.astimezone(timezone('Europe/Moscow'))
            last_visit = last_visit.strftime('%Y-%m-%d %H:%M:%S')
        else:
            last_visit = ''
        month_gb_quota = user.get('MonthlyQuotaRemainingGB')
        problems = user.get('Problems')
        status = user.get('Status')
        user_name = shorten_name(user.get('UserName'))
        status_icon = '🟢' if status == 'green' else '🔴'
        problems_string = f'⛔: {problems} ' if problems else ''
        time_string = f'🕐: {last_visit}\n\n' if last_visit else '\n'

        result_message = (
            f'{status_icon} : {user_name} '
            f'{problems_string}'
            f'🔃: {month_gb_quota} GB\n'
            f'{time_string}'
        )

        result.append(result_message)
    await message.answer(text=''.join(result))
