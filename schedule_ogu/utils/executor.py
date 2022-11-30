import asyncio
from contextlib import suppress

from aiogram import Dispatcher
from aiogram.utils.exceptions import TelegramAPIError
from aiogram.utils.executor import Executor
from loguru import logger

from schedule_ogu import UserModel
from schedule_ogu.config import bot_config
from schedule_ogu.misc import dp
from schedule_ogu.services.schedule import ScheduleService
from schedule_ogu.utils import db

runner = Executor(dp)


class DisplayManager:
    display = None

    @classmethod
    def run_display(cls):
        if not bot_config.has_display:
            from pyvirtualdisplay import Display

            cls.display = Display(visible=False, size=(800, 800))
            logger.warning("Display started")
            cls.display.start()
            logger.warning("Display started")

    @classmethod
    async def close_display(cls, _: Dispatcher):
        if not bot_config.has_display:
            if cls.display:
                cls.display.stop()


# async def on_startup_webhook(dispatcher: Dispatcher):
#     logger.info("Configure Web-Hook URL to: {url}", url=config.WEBHOOK_URL)
#     await dispatcher.bot.set_webhook(config.WEBHOOK_URL)


async def on_startup_notify(dispatcher: Dispatcher):
    for user in await UserModel.filter(is_superuser=True).all():
        with suppress(TelegramAPIError):
            await dispatcher.bot.send_message(
                chat_id=user.id, text="Bot started", disable_notification=True
            )
            logger.info("Notified superuser {user} about bot is started.", user=user.id)
        await asyncio.sleep(0.2)


def setup():
    logger.info("Configure executor...")
    db.setup(runner)
    ScheduleService.setup(runner)
    if not bot_config.has_display:
        DisplayManager.run_display()
        runner.on_shutdown(DisplayManager.close_display)
    # join_list.setup(runner)
    # apscheduller.setup(runner)
    # healthcheck.setup(runner)
    # runner.on_startup(on_startup_webhook, webhook=True, polling=False)
    if bot_config.superuser_startup_notifier:
        runner.on_startup(on_startup_notify)
