from aiogram import Dispatcher
from ScheduleOGU import Client


__all__ = ('dp', 'bot')


bot = Client()
dp = Dispatcher(bot, storage=bot.storage)
