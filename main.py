import asyncio
import logging

from aiogram import types, Dispatcher
from aiogram.utils import executor
from tabulate import tabulate

from ScheduleOGU import DayType, Client
from ScheduleOGU.utils.logging import CustomFormatter


logging.getLogger('aiogram')
logging.getLogger("ScheduleOGU.core.http")
logging.getLogger("tortoise.db_client")
handler = logging.StreamHandler()
handler.setFormatter(CustomFormatter())
logging.basicConfig(level=logging.INFO, handlers=[handler])

log = logging.getLogger()

bot = Client()
dp = Dispatcher(bot)


@dp.message_handler(commands={'monday', 'Monday', 'понедельник', 'Понедельник'})
async def monday(message: types.Message):
    schedule = await bot.get_schedule(7961)

    rows = [[subject] for subject in schedule[DayType.Monday]]
    table = tabulate(rows, headers=[DayType.Monday.name], tablefmt="simple")
    await message.reply(table, parse_mode=types.ParseMode.HTML)


@dp.message_handler(commands=['tuesday', 'Tuesday', 'вторник', 'Вторник'])
async def tuesday(message: types.Message):
    schedule = await bot.get_schedule(7961)

    rows = [[subject] for subject in schedule[DayType.Thursday]]
    table = tabulate(rows, headers=[DayType.Thursday.name], tablefmt="simple")
    await message.reply(table, parse_mode=types.ParseMode.HTML)


@dp.message_handler(commands=['wednesday', 'Wednesday', 'среда', 'Среда'])
async def wednesday(message: types.Message):
    schedule = await bot.get_schedule(7961)

    rows = [[subject] for subject in schedule[DayType.Wednesday]]
    table = tabulate(rows, headers=[DayType.Wednesday.name], tablefmt="simple")
    await message.reply(table, parse_mode=types.ParseMode.HTML)


@dp.message_handler(commands=['thursday', 'Thursday', 'четверг', 'Четверг'])
async def thursday(message: types.Message):
    schedule = await bot.get_schedule(7961)

    rows = [[subject] for subject in schedule[DayType.Thursday]]
    table = tabulate(rows, headers=[DayType.Thursday.name], tablefmt="simple")
    await message.reply(table, parse_mode=types.ParseMode.HTML)


@dp.message_handler(commands=['friday', 'Friday', 'пятница', 'Пятница'])
async def friday(message: types.Message):
    schedule = await bot.get_schedule(7961)

    rows = [[subject] for subject in schedule[DayType.Friday]]
    table = tabulate(rows, headers=[DayType.Friday.name], tablefmt="simple")
    await message.reply(table, parse_mode=types.ParseMode.HTML)


@dp.message_handler(commands=['saturday', 'Saturday', 'суббота', 'Суббота'])
async def saturday(message: types.Message):
    schedule = await bot.get_schedule(7961)

    rows = [[subject] for subject in schedule[DayType.Saturday]]
    table = tabulate(rows, headers=[DayType.Saturday.name], tablefmt="simple")
    await message.reply(table, parse_mode=types.ParseMode.HTML)


@dp.message_handler(commands=['week', 'Week', 'неделя', 'Неделя'])
async def week(message: types.Message):
    schedule = await bot.get_schedule(7961)
    for day, subjects in schedule.items():
        rows = [[subject] for subject in subjects]
        table = tabulate(rows, headers=[day.name], tablefmt="simple")
        await message.reply(table, parse_mode=types.ParseMode.HTML)


@dp.message_handler(commands=['refresh', 'restart'])
async def refresh(message: types.Message):
    await bot.fetch_schedule(7961)
    await message.reply("Successfully Refreshed")


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    loop.run_until_complete(bot.http.static_login())
    loop.run_until_complete(bot.connect_db())
    executor.start_polling(dp, skip_updates=True)
