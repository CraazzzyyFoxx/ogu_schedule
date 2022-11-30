from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

commands_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton('Расписание на вчера'), KeyboardButton('Расписание на сегодня'), KeyboardButton('Расписание на завтра')],
        [KeyboardButton('Экзамены')]
    ],
    resize_keyboard=True
)
