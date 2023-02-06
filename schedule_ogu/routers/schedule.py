import datetime

from aiogram import types
from aiogram.types import Message

from aiogram import Router
from aiogram.filters import Text, Command

from schedule_ogu.services.schedule import ScheduleService
from schedule_ogu.models.db import UserModel
from schedule_ogu.models.enums import DayType
from schedule_ogu.utils.render import RendererSchedule
from schedule_ogu.utils.time import ScheduleTime


router = Router()


async def user_in_db(message: Message) -> UserModel | None:
    user = await UserModel.filter(id=message.from_user.id).first()

    if not user:
        await message.reply("Используйте команду /start.")
        return None
    return user


async def send_schedule(message: types.Message, day: DayType, future: bool = False):
    user = await user_in_db(message)
    if user:
        week_delta = 0
        week_day = datetime.datetime.utcnow().weekday()
        if future and week_day >= day:
            week_delta += 1

        ...
        schedule = await ScheduleService.get_schedule(user, week_delta=week_delta)
        await message.reply(RendererSchedule.render_day(user=user, schedule=schedule, day=day),
                            disable_web_page_preview=True)


async def send_exams(message: types.Message):
    user = await user_in_db(message)
    if not user:
        return
    await message.reply(RendererSchedule.render_exams(user, await ScheduleService.get_exams(user)),
                        disable_web_page_preview=True)


@router.message(Command(commands=['previous', 'вчера']))
async def cmd_previous(message: types.Message):
    await send_schedule(message, ScheduleTime.previous_day())


@router.message(Command(commands=['today', 'сегодня']))
async def cmd_today(message: types.Message):
    await send_schedule(message, ScheduleTime.today())


@router.message(Command(commands=['next', 'завтра']))
async def cmd_next(message: types.Message):
    await send_schedule(message, ScheduleTime.next_day(), future=True)


@router.message(Command(commands=['exams', 'экзамены', 'Экзамены']))
async def cmd_exams(message: types.Message):
    await send_exams(message)


@router.message(Text(text='Расписание на сегодня', ignore_case=True))
async def kb_today(message: types.Message):
    await send_schedule(message, ScheduleTime.today())


@router.message(Text(text='Расписание на завтра', ignore_case=True))
async def kb_next(message: types.Message):
    await send_schedule(message, ScheduleTime.next_day(), future=True)


@router.message(Text(text='Расписание на вчера', ignore_case=True))
async def kb_next(message: types.Message):
    await send_schedule(message, ScheduleTime.previous_day())


@router.message(Text(text='Экзамены', ignore_case=True))
async def kb_exams(message: types.Message):
    await send_exams(message)


@router.message(Command(commands=['monday', 'Monday', 'понедельник', 'Понедельник']))
async def monday(message: types.Message):
    await send_schedule(message, DayType.Monday)


@router.message(Command(commands=['tuesday', 'Tuesday', 'вторник', 'Вторник']))
async def tuesday(message: types.Message):
    await send_schedule(message, DayType.Tuesday)


@router.message(Command(commands=['wednesday', 'Wednesday', 'среда', 'Среда']))
async def wednesday(message: types.Message):
    await send_schedule(message, DayType.Wednesday)


@router.message(Command(commands=['thursday', 'Thursday', 'четверг', 'Четверг']))
async def thursday(message: types.Message):
    await send_schedule(message, DayType.Thursday)


@router.message(Command(commands=['friday', 'Friday', 'пятница', 'Пятница']))
async def friday(message: types.Message):
    await send_schedule(message, DayType.Friday)


@router.message(Command(commands=['saturday', 'Saturday', 'суббота', 'Суббота']))
async def saturday(message: types.Message):
    await send_schedule(message, DayType.Saturday)

# @router.message(Command(commands=['week', 'Week', 'неделя', 'Неделя']))
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
