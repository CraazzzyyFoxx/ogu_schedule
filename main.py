import asyncio
import logging

from aiogram import types, Dispatcher
from aiogram.utils import executor
from ScheduleOGU import DayType, Client, print_schedule
from ScheduleOGU.utils.logging import CustomFormatter


logging.getLogger('aiogram')
logging.getLogger("ScheduleOGU.core.http")
logging.getLogger("tortoise.db_client").setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setFormatter(CustomFormatter())
logging.basicConfig(level=logging.INFO, handlers=[handler])

log = logging.getLogger()

bot = Client()
dp = Dispatcher(bot)


@dp.message_handler(commands={'monday', 'Monday', 'понедельник', 'Понедельник'})
async def monday(message: types.Message):
    schedule = await bot.get_schedule(7961)
    await message.reply(print_schedule(schedule, DayType.Monday), parse_mode=types.ParseMode.HTML)


@dp.message_handler(commands=['tuesday', 'Tuesday', 'вторник', 'Вторник'])
async def tuesday(message: types.Message):
    schedule = await bot.get_schedule(7961)
    await message.reply(print_schedule(schedule, DayType.Tuesday), parse_mode=types.ParseMode.HTML)


@dp.message_handler(commands=['wednesday', 'Wednesday', 'среда', 'Среда'])
async def wednesday(message: types.Message):
    schedule = await bot.get_schedule(7961)
    await message.reply(print_schedule(schedule, DayType.Wednesday), parse_mode=types.ParseMode.HTML)


@dp.message_handler(commands=['thursday', 'Thursday', 'четверг', 'Четверг'])
async def thursday(message: types.Message):
    schedule = await bot.get_schedule(7961)
    await message.reply(print_schedule(schedule, DayType.Thursday), parse_mode=types.ParseMode.HTML)


@dp.message_handler(commands=['friday', 'Friday', 'пятница', 'Пятница'])
async def friday(message: types.Message):
    schedule = await bot.get_schedule(7961)
    await message.reply(print_schedule(schedule, DayType.Friday), parse_mode=types.ParseMode.HTML)


@dp.message_handler(commands=['saturday', 'Saturday', 'суббота', 'Суббота'])
async def saturday(message: types.Message):
    schedule = await bot.get_schedule(7961)
    await message.reply(print_schedule(schedule, DayType.Saturday), parse_mode=types.ParseMode.HTML)


@dp.message_handler(commands=['week', 'Week', 'неделя', 'Неделя'])
async def week(message: types.Message):
    schedule = await bot.get_schedule(7961)
    for day in schedule.keys():
        await message.reply(print_schedule(schedule, day), parse_mode=types.ParseMode.HTML)


@dp.message_handler(commands=['refresh', 'restart'])
async def refresh(message: types.Message):
    await bot.fetch_schedule(7961)
    await message.reply("Successfully Refreshed")


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    loop.run_until_complete(bot.http.static_login())
    loop.run_until_complete(bot.connect_db())
    executor.start_polling(dp, skip_updates=True)
