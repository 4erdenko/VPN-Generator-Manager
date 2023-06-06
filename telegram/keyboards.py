from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

main_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
main_keyboard.add(KeyboardButton(text='🔐 Make config'), '📝 Get users')
main_keyboard.add(KeyboardButton(text='❌ Delete user'))
