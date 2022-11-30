from aiogram import Dispatcher
from aiogram.utils.executor import Executor
from loguru import logger
from tortoise import Tortoise

from schedule_ogu.config import tortoise_config


async def on_startup(dispatcher: Dispatcher):
    await Tortoise.init(config=tortoise_config)
    await Tortoise.generate_schemas()


async def on_shutdown(dispatcher: Dispatcher):
    await Tortoise.close_connections()


def setup(executor: Executor):
    executor.on_startup(on_startup)
    executor.on_shutdown(on_shutdown)