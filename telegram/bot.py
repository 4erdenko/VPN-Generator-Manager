import functools
import logging
import os

import aiogram
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ParseMode

from config import BOT_API, CHAT_ID, START_MSG
from telegram.keyboards import main_keyboard
from telegram.users_handler import User
from vpnworks.api import VpnWorksApi

bot = aiogram.Bot(token=BOT_API, parse_mode=ParseMode.HTML)
dp = aiogram.Dispatcher(bot, storage=MemoryStorage())

logger = logging.getLogger(__name__)

client = VpnWorksApi()


def restricted(func):
    """
    Decorator to restrict the execution of a command only to
     a user with a certain ID.

    Args:
        func (function): The function to be decorated.

    Returns:
        function: The decorated function.
    """

    @functools.wraps(func)
    async def wrapped(message: aiogram.types.Message, *args, **kwargs):
        if message.from_user.id != CHAT_ID:
            return
        return await func(message, *args, **kwargs)

    return wrapped


class DeleteUserState(StatesGroup):
    """
    A state group for tracking the process of a user deletion.
    """

    waiting_for_user_id = State()


@dp.message_handler(commands=['start'])
@restricted
async def start(message: aiogram.types.Message):
    """
    The handler for the 'start' command. Sends a greeting message to the user.

    Args:
        message (aiogram.types.Message): The message from the user.
    """
    await message.answer(START_MSG, reply_markup=main_keyboard)
    logger.info(f'User {message.from_user.id} started bot')


@dp.message_handler(Text(equals='🔐 Make config'))
@restricted
async def get_config(message: aiogram.types.Message):
    """
    The handler for the 'Make config' command. Sends a
    configuration file to the user.

    Args:
        message (aiogram.types.Message): The message from the user.
    """
    filename, username = await client.create_conf_file()
    users_dict = await client.get_users_dict()
    person_name = users_dict.get(f'{username}').get('PersonName')
    person_desc = users_dict.get(f'{username}').get('PersonDesc')
    person_link = users_dict.get(f'{username}').get('PersonDescLink')
    caption_message = (
        f'<code>{username}</code>'
        f'\n\n<a href="{person_link}">{person_name}</a>'
        f'\n{person_desc}'
    )
    try:
        with open(filename, 'rb') as file:
            await message.answer_document(file, caption=caption_message)
    except Exception as error:
        return await message.answer(str(error))
    os.remove(filename)
    logger.info(f'User {message.from_user.id} get config {filename}')


@dp.message_handler(Text(equals='📝 Get users'))
@restricted
async def get_users(message: aiogram.types.Message):
    """
    The handler for the 'Get users' command. Sends a list of users to the user.

    Args:
        message (aiogram.types.Message): The message from the user.
    """
    wait_message = await message.answer('Getting users...')
    user_data = await client.get_users()

    users = [User(data) for data in user_data]
    result = [user.format_message() for user in users]
    deactive_users = len(
        [user for user in users if not user.is_active and user.has_visited]
    )
    not_entered_users = len(
        [user for user in users if not user.is_active and not user.has_visited]
    )
    low_gb_quota_names = [user.name for user in users if user.has_low_quota]
    stats = await client.get_users_stats()
    active_users = stats.get('ActiveUsers').pop().get('Value')
    total_users = stats.get('TotalUsers').pop().get('Value')
    total_gb_quota = stats.get('TotalTrafficGB').pop().get('Value')

    low_quota_info = (
        f'<b>Low quota:</b> {" | ".join(low_gb_quota_names)}'
        if low_gb_quota_names
        else ''
    )
    summary_message = (
        f'<b>Total users:</b> {total_users}\n'
        f'<b>Active:</b> {active_users} | <b>Deactive:</b> {deactive_users} | '
        f'<b>Not entered:</b> {not_entered_users}\n'
        f'<b>Total quota:</b> {total_gb_quota}\n'
        f'{low_quota_info}'
    )

    result.append(summary_message)

    await bot.edit_message_text(
        message_id=wait_message.message_id,
        chat_id=wait_message.chat.id,
        text=''.join(result),
    )
    logger.info(f'User {message.from_user.id} get users')


@dp.message_handler(Text(equals='❌ Delete user'))
@restricted
async def start_delete_user(message: aiogram.types.Message):
    """
    The handler for the 'Delete user' command. It asks the user to
    enter a user ID for deletion.

    Args:
        message (aiogram.types.Message): The message from the user.
    """
    try:
        await message.answer('Enter user ID')
        await DeleteUserState.waiting_for_user_id.set()
        logger.info(f'User {message.from_user.id} start delete user')
    except Exception as e:
        await message.answer(f'Error: while start deleting user: {e}')
        logger.error(f'Error: while deleting user: {e}')


@dp.message_handler(state=DeleteUserState.waiting_for_user_id)
@restricted
async def delete_user_id(message: aiogram.types.Message, state: FSMContext):
    """
    The handler for the deletion of a user ID. It receives the ID from
    the user, attempts to delete the user
    with this ID and sends a result message to the user.

    Args:
        message (aiogram.types.Message): The message from the user.
        state (FSMContext): The finite state machine context to
        manage the states of the conversation.
    """
    user_id = await client.get_user_id(message.text)
    if user_id and await client.delete_user(user_id) is not None:
        await message.answer('User deleted')
        logger.info(f'User {message.from_user.id} deleted user {user_id}')
    else:
        await message.answer('User not found')
        logger.info(f'User {message.from_user.id} not found user {user_id}')
    await state.reset_state(with_data=True)
    await state.finish()
    logger.info(f'User {message.from_user.id} finish delete user')
