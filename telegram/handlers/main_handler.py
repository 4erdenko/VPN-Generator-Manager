import logging

import aiogram
from aiogram import Bot, Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from config import START_MSG
from telegram.filters.custom_filter import IsAdmin
from telegram.utils import User, send_configs
from vpnworks.api import VpnWorksApi

logger = logging.getLogger(__name__)
client = VpnWorksApi()
router = Router()

router.message.filter(IsAdmin())


class DeleteUserState(StatesGroup):
    """
    A state group for tracking the process of a user deletion.
    """

    waiting_for_user_id = State()


@router.message(CommandStart())
async def start(message: aiogram.types.Message):
    """
    The handler for the 'start' command. Sends a greeting message to the user.

    Args:
        message (aiogram.types.Message): The message from the user.
    """
    await message.answer(START_MSG)
    logger.info(f'User {message.from_user.id} started bot')


@router.message(Command(commands='make_config'))
async def get_config(message: aiogram.types.Message, bot: Bot):
    """
    The handler for the 'Make config' command. Sends a
    configuration file to the user.

    Args:
        message (aiogram.types.Message): The message from the user.
        :param message:
        :param bot:
    """
    await send_configs(client, message, bot)


@router.message(Command(commands='get_users'))
async def get_users(message: aiogram.types.Message, bot: Bot):
    """
    The handler for the 'Get users' command. Sends a list of users to the user.

    Args:
        message (aiogram.types.Message): The message from the user.
        :param message:
        :param bot:
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


@router.message(Command(commands='delete_user'))
async def start_delete_user(message: aiogram.types.Message, state: FSMContext):
    """
    The handler for the 'Delete user' command. It asks the user to
    enter a user ID for deletion.

    Args:
        message (aiogram.types.Message): The message from the user.
        :param message:
        :param state:
    """
    try:
        await message.answer('Enter user ID')
        await state.set_state(DeleteUserState.waiting_for_user_id)
        logger.info(f'User {message.from_user.id} start delete user')
    except Exception as e:
        await message.answer(f'Error: while start deleting user: {e}')
        logger.error(f'Error: while deleting user: {e}')


@router.message(DeleteUserState.waiting_for_user_id)
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
    await state.clear()
    logger.info(f'User {message.from_user.id} finish delete user')
