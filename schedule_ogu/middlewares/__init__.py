import logging

from aiogram import Dispatcher
from aiogram.contrib.middlewares.logging import LoggingMiddleware

_log = logging.getLogger(__name__)


def setup(dispatcher: Dispatcher):
    _log.info("Configure middlewares...")
    # from schedule_ogu.misc import i18n

    dispatcher.middleware.setup(LoggingMiddleware("bot"))
    # dispatcher.middleware.setup(i18n)
