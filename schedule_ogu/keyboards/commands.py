from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder

import config


builder = ReplyKeyboardBuilder()


builder.button(text='Расписание на вчера')
builder.button(text='Расписание на сегодня')
builder.button(text='Расписание на завтра')


if config.UNABLE_EXAM_BUTTON:
    builder.button(text='Экзамены')

builder.adjust(3)


commands_kb = builder.as_markup(resize_keyboard=True)


