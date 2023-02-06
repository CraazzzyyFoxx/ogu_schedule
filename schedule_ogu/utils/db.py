from __future__ import annotations

from tortoise import Tortoise
from aiogram import Dispatcher, Bot

from config import tortoise_config


# async def on_startup(dispatcher: Dispatcher):
#     await Tortoise.init(config=tortoise_config)
#     await Tortoise.generate_schemas()
#
#
# async def on_shutdown(dispatcher: Dispatcher):
#     await Tortoise.close_connections()


async def setup(bot: Bot):
    await Tortoise.init(config=tortoise_config)
    await Tortoise.generate_schemas()

