import asyncio
from contextlib import suppress

from aiogram import Bot, Dispatcher
from aiogram.exceptions import TelegramAPIError
from aiogram.fsm.storage.memory import MemoryStorage
from loguru import logger
from tortoise import Tortoise

from config import bot_config, tortoise_config
from schedule_ogu.models.db import UserModel
from schedule_ogu.routers import start, schedule
from schedule_ogu.services.schedule import ScheduleService


class DisplayManager:
    display = None

    @classmethod
    def run_display(cls):
        if not bot_config.has_display:
            from pyvirtualdisplay.display import Display

            cls.display = Display(visible=False, size=(800, 800))
            cls.display.start()
            logger.warning("Display started")

    @classmethod
    async def close_display(cls, _: Dispatcher):
        if not bot_config.has_display:
            if cls.display:
                cls.display.stop()


async def on_startup_notify(bot: Bot):
    for user in await UserModel.filter(is_superuser=True).all():
        with suppress(TelegramAPIError):
            await bot.send_message(
                chat_id=user.id, text="Bot started", disable_notification=True
            )
            logger.info("Notified superuser {user} about bot is started.", user=user.id)
        await asyncio.sleep(0.2)


async def setup():
    bot = Bot(bot_config.token, parse_mode="HTML")
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    logger.info("Configure routers...")

    dp.include_router(start.router)
    dp.include_router(schedule.router)

    if not bot_config.has_display:
        DisplayManager.run_display()

    await Tortoise.init(config=tortoise_config)
    await Tortoise.generate_schemas()

    await ScheduleService.setup(bot)

    if bot_config.superuser_startup_notifier:
        await on_startup_notify(bot)

    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
