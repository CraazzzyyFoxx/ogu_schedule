from pathlib import Path

from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from loguru import logger

from schedule_ogu.config import bot_config
# from aiogram_bot.middlewares.i18n import I18nMiddleware

app_dir: Path = Path(__file__).parent.parent
locales_dir = app_dir / "locales"

bot = Bot(bot_config.token, parse_mode=types.ParseMode.HTML)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
# i18n = I18nMiddleware("bot", locales_dir, default="en")

# if config.SENTRY_URL:
#     logger.info("Setup Sentry SDK")
#     sentry_sdk.init(
#         config.SENTRY_URL,
#         traces_sample_rate=1.0,
#     )


def setup():
    from schedule_ogu import filters, middlewares
    from schedule_ogu.utils import executor
    from schedule_ogu.services.schedule import ScheduleService

    middlewares.setup(dp)
    filters.setup(dp)
    executor.setup()


    logger.info("Configure handlers...")
    # noinspection PyUnresolvedReferences
    import schedule_ogu.handlers
