from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

# Main keyboard
main_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
"""
main_keyboard: ReplyKeyboardMarkup object for the bot's main menu. 

This keyboard contains three options:
1. Make config - To make a configuration.
2. Get users - To get the list of all users.
3. Delete user - To delete a user.
"""

# Add buttons to the main keyboard
main_keyboard.add(KeyboardButton(text='🔐 Make config'), '📝 Get users')
"""
Add the 'Make config' and 'Get users' buttons to the main keyboard.
"""

main_keyboard.add(KeyboardButton(text='❌ Delete user'))
"""
Add the 'Delete user' button to the main keyboard.
"""
