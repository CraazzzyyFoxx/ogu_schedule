import logging

from ScheduleOGU.main import bot
from aiogram import executor
from ScheduleOGU.handlers import dp
from ScheduleOGU.utils.logging import CustomFormatter

if __name__ == '__main__':
    logging.getLogger('aiogram')
    logging.getLogger("ScheduleOGU.core.http")
    logging.getLogger("tortoise.db_client").setLevel(logging.DEBUG)
    handler = logging.StreamHandler()
    handler.setFormatter(CustomFormatter())
    logging.basicConfig(level=logging.INFO, handlers=[handler])

    log = logging.getLogger()
    executor.start_polling(dp,
                           skip_updates=True,
                           on_startup=bot.on_startup,
                           on_shutdown=bot.on_shutdown)
