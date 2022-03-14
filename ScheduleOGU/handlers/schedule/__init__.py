import typing as t

from aiogram import types

from ScheduleOGU import print_schedule, UserModel, DayType, ScheduleDayModel
from main import dp


@dp.message_handler(commands={'monday', 'Monday', 'понедельник', 'Понедельник'})
async def monday(message: types.Message):
    await message.reply(print_schedule((await dp.bot.get_schedule_for_user(message)), DayType.Monday).__str__(),
                        parse_mode=types.ParseMode.HTML,
                        disable_web_page_preview=True)


@dp.message_handler(commands=['tuesday', 'Tuesday', 'вторник', 'Вторник'])
async def tuesday(message: types.Message):
    await message.reply(print_schedule(await dp.bot.get_schedule_for_user(message), DayType.Tuesday).__str__(),
                        parse_mode=types.ParseMode.HTML,
                        disable_web_page_preview=True)


@dp.message_handler(commands=['wednesday', 'Wednesday', 'среда', 'Среда'])
async def wednesday(message: types.Message):
    await message.reply(print_schedule(await dp.bot.get_schedule_for_user(message), DayType.Wednesday).__str__(),
                        parse_mode=types.ParseMode.HTML,
                        disable_web_page_preview=True)


@dp.message_handler(commands=['thursday', 'Thursday', 'четверг', 'Четверг'])
async def thursday(message: types.Message):
    await message.reply(print_schedule(await dp.bot.get_schedule_for_user(message), DayType.Thursday).__str__(),
                        parse_mode=types.ParseMode.HTML,
                        disable_web_page_preview=True)


@dp.message_handler(commands=['friday', 'Friday', 'пятница', 'Пятница'])
async def friday(message: types.Message):
    await message.reply(print_schedule(await dp.bot.get_schedule_for_user(message), DayType.Friday).__str__(),
                        parse_mode=types.ParseMode.HTML,
                        disable_web_page_preview=True)


@dp.message_handler(commands=['saturday', 'Saturday', 'суббота', 'Суббота'])
async def saturday(message: types.Message):
    await message.reply(print_schedule(await dp.bot.get_schedule_for_user(message), DayType.Saturday).__str__(),
                        parse_mode=types.ParseMode.HTML,
                        disable_web_page_preview=True)


@dp.message_handler(commands=['week', 'Week', 'неделя', 'Неделя'])
async def week(message: types.Message):
    schedule: t.List[ScheduleDayModel] = await dp.bot.get_schedule_for_user(message)
    for day in schedule:
        await message.reply(print_schedule(schedule, day.day).__str__(),
                            parse_mode=types.ParseMode.HTML,
                            disable_web_page_preview=True)


@dp.message_handler(commands=['refresh', 'restart'])
async def refresh(message: types.Message):
    user = await UserModel.filter(id=message.from_user.id).first()

    if user is None:
        await message.reply("Используйте команду /start.")
    await dp.bot.fetch_schedule(user.group_id)
    await message.reply("Successfully Refreshed")
