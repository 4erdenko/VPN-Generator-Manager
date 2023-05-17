import os
from datetime import datetime

import aiogram
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import ParseMode
from pytz import timezone

from api.vpn_generator import (
    make_config,
    get_user,
    shorten_name,
    delete_user,
    get_user_id_by_name,
)
from config import BOT_API, CHAT_ID
from telegram.keyboards import main_keyboard

bot = aiogram.Bot(token=BOT_API, parse_mode=ParseMode.HTML)
dp = aiogram.Dispatcher(bot, storage=MemoryStorage())


class DeleteUserState(StatesGroup):
    waiting_for_user_id = State()


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
        user_id = user.get('UserID')
        month_gb_quota = user.get('MonthlyQuotaRemainingGB')
        problems = user.get('Problems')
        status = user.get('Status')
        user_name = shorten_name(user.get('UserName'))
        status_icon = '🟢' if status == 'green' else '🔴'
        problems_string = f'⛔: {problems} ' if problems else ''
        time_string = f'🕐: {last_visit}\n' if last_visit else ''

        result_message = (
            f'{status_icon} : {user_name} '
            f'{problems_string}'
            f'🔃: {month_gb_quota} GB\n'
            f'{time_string}\n'
        )

        result.append(result_message)
    await message.answer(text=''.join(result))


@dp.message_handler(Text(equals='❌ Delete user'))
async def start_delete_user(message: aiogram.types.Message):
    await message.answer('Enter user ID')
    await DeleteUserState.waiting_for_user_id.set()


@dp.message_handler(state=DeleteUserState.waiting_for_user_id)
async def delete_user_id(message: aiogram.types.Message, state: FSMContext):
    user_id = get_user_id_by_name(message.text)
    if user_id and delete_user(user_id):
        await message.answer('User deleted')
    else:
        await message.answer('User not found')
    await state.reset_state(with_data=True)
    await state.finish()
