from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder

# Инициализируем билдер для основной клавиатуры
main_kb_builder = ReplyKeyboardBuilder()

# Создаем кнопки основной клавиатуры
button_make_config = KeyboardButton(text='🔐 Make config')
button_get_users = KeyboardButton(text='📝 Get users')
button_delete_user = KeyboardButton(text='❌ Delete user')

# Добавляем кнопки в билдер
main_kb_builder.add(button_make_config, button_get_users)
main_kb_builder.add(button_delete_user)

# Создаем клавиатуру из билдера
main_keyboard: ReplyKeyboardMarkup = main_kb_builder.as_markup(
    resize_keyboard=True
)
