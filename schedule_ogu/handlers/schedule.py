from aiogram import types
from aiogram.types import Message

from schedule_ogu.services.schedule import ScheduleService
from schedule_ogu import UserModel, DayType, ScheduleTime
from schedule_ogu.utils.render import RendererSchedule
from schedule_ogu.misc import dp


async def user_in_bot(message: Message):
    user = await UserModel.filter(id=message.from_user.id).first()

    if not user:
        await message.reply("Используйте команду /start.")
        return False
    return user


async def send_schedule(message: types.Message, day: DayType, past=False):
    user = await user_in_bot(message)
    if not user:
        return
    await message.reply(RendererSchedule.render_day(user, await ScheduleService.get_schedule_day(user, day, past=past)),
                        parse_mode=types.ParseMode.HTML,
                        disable_web_page_preview=True)


async def send_exams(message: types.Message):
    user = await user_in_bot(message)
    if not user:
        return
    await message.reply(RendererSchedule.render_exams(user, await ScheduleService.get_exams(user)),
                        parse_mode=types.ParseMode.HTML,
                        disable_web_page_preview=True)


@dp.message_handler(commands=['previous', 'вчера'])
async def cmd_today(message: types.Message):
    await send_schedule(message, ScheduleTime.previous_day())


@dp.message_handler(commands=['today', 'сегодня'])
async def cmd_today(message: types.Message):
    await send_schedule(message, ScheduleTime.today())


@dp.message_handler(commands=['next', 'завтра'])
async def cmd_next(message: types.Message):
    await send_schedule(message, ScheduleTime.next_day())


@dp.message_handler(commands=['exams', 'экзамены', 'Экзамены'])
async def cmd_exams(message: types.Message):
    await send_exams(message)


@dp.message_handler(text_contains='Расписание на сегодня')
async def kb_today(message: types.Message):
    await send_schedule(message, ScheduleTime.today())


@dp.message_handler(text_contains='Расписание на завтра')
async def kb_next(message: types.Message):
    await send_schedule(message, ScheduleTime.next_day())


@dp.message_handler(text_contains='Расписание на вчера')
async def kb_next(message: types.Message):
    await send_schedule(message, ScheduleTime.previous_day(), past=True)


@dp.message_handler(text_contains='Экзамены')
async def kb_exams(message: types.Message):
    await send_exams(message)


@dp.message_handler(commands={'monday', 'Monday', 'понедельник', 'Понедельник'})
async def monday(message: types.Message):
    await send_schedule(message, DayType.Monday)


@dp.message_handler(commands=['tuesday', 'Tuesday', 'вторник', 'Вторник'])
async def tuesday(message: types.Message):
    await send_schedule(message, DayType.Tuesday)


@dp.message_handler(commands=['wednesday', 'Wednesday', 'среда', 'Среда'])
async def wednesday(message: types.Message):
    await send_schedule(message, DayType.Wednesday)


@dp.message_handler(commands=['thursday', 'Thursday', 'четверг', 'Четверг'])
async def thursday(message: types.Message):
    await send_schedule(message, DayType.Thursday)


@dp.message_handler(commands=['friday', 'Friday', 'пятница', 'Пятница'])
async def friday(message: types.Message):
    await send_schedule(message, DayType.Friday)


@dp.message_handler(commands=['saturday', 'Saturday', 'суббота', 'Суббота'])
async def saturday(message: types.Message):
    await send_schedule(message, DayType.Saturday)

# @dp.message_handler(commands=['week', 'Week', 'неделя', 'Неделя'])
# async def week(message: types.Message):
#     schedule: typing.List[ScheduleSubjectModel] = await get_schedule(message)
#     data = {}
#     for day in DayType:
#         data[day] = []
#     for day_schedule in schedule:
#         data[day_schedule.day].append(day_schedule)
#     logger.warning(data)
#     for data_ in data.values():
#         await message.reply(RendererSchedule.render_day(data_),
#                             parse_mode=types.ParseMode.HTML,
#                             disable_web_page_preview=True)
