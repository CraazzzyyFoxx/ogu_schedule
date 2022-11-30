from aiogram import __main__ as aiogram_core
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import CommandHelp
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.utils.markdown import hbold, hlink, quote_html
from loguru import logger

from schedule_ogu import UserType
from schedule_ogu.keyboards import start
from schedule_ogu.keyboards.commands import commands_kb
from schedule_ogu.misc import dp, bot
from schedule_ogu.models import UserModel


class StartForm(StatesGroup):
    user_type = State()
    faculty = State()
    department = State()
    group = State()
    course = State()
    employee = State()


@dp.message_handler(chat_type=types.ChatType.PRIVATE, commands=["start"])
async def cmd_start(message: types.Message):
    logger.info("User {user} start conversation with bot", user=message.from_user.id)
    await message.answer(
        f"Привет, {hbold(message.from_user.full_name)}.\n"
        f"Отправь /help если ты хочешь увидеть список команд\n"
        f"Мой исходный код: {hlink('GitHub', 'https://github.com/CraazzzyyFoxx/ogu_schedule')} \n"

    )
    state = dp.current_state(user=message.from_user.id)
    await state.set_state(StartForm.user_type)
    await message.answer("Студент или Преподаватель?", reply_markup=start.start_kb_choose_user_type)


@dp.message_handler(chat_type=types.ChatType.GROUP, commands=["start"])
async def cmd_start(message: types.Message):
    await message.answer(
        f"Привет, {hbold(message.from_user.full_name)}.\n"
        f"Отправь /help если ты хочешь увидеть список команд\n"
        f"Мой исходный код: {hlink('GitHub', 'https://github.com/CraazzzyyFoxx/ogu_schedule')} \n\n"
        f"{hbold('Регистрация доступна только в лс')}"

    )


@dp.message_handler(CommandHelp())
async def cmd_help(message: types.Message):
    logger.info("User {user} read help in {chat}", user=message.from_user.id, chat=message.chat.id)
    text = [
        hbold("Здесь ты можешь увидить список моих команд:"),
        "{command} - Получите это сообщение".format(command="/help"),
        "{command} - My version".format(command="/version"),
        "",
    ]

    if message.chat.type in {types.ChatType.PRIVATE}:
        text.extend([hbold("Доступно только в лс:"),
                     "{command} - Начните разговор с ботом".format(command="/start"),
                     "",
                     ])
    await message.reply("\n".join(text))


@dp.callback_query_handler(start.cb_user_start.filter(property="user_type"), state=StartForm.user_type)
async def cq_start_choose_user_type(query: types.CallbackQuery, state: FSMContext, callback_data: dict):
    logger.info(
        "User {user} changed user_type to {user_type}",
        user=query.from_user.id,
        user_type=callback_data["value"]
    )
    await state.update_data(user_type=callback_data["value"])
    await state.set_state(StartForm.faculty)
    markup = await start.start_kb_choose_faculty()
    await query.message.edit_text("Выберите факультет", reply_markup=markup)


@dp.callback_query_handler(start.cb_user_start.filter(property="faculty"), state=StartForm.faculty)
async def cq_start_choose_faculty(query: types.CallbackQuery, state: FSMContext, callback_data: dict):
    logger.info(
        "User {user} changed  faculty to {faculty_id}",
        user=query.from_user.id,
        faculty_id=callback_data["value"]
    )
    await state.update_data(faculty=callback_data["value"])
    data = await state.get_data()
    if int(data["user_type"]) is UserType.Student.value:
        await state.set_state(StartForm.course)
        markup = await start.start_kb_choose_course()
        await query.message.edit_text("Выберите курс", reply_markup=markup)
    else:
        await state.set_state(StartForm.department)
        markup = await start.start_kb_choose_department(int(callback_data["value"]))
        await query.message.edit_text("Выберите кафедру", reply_markup=markup)


@dp.callback_query_handler(start.cb_user_start.filter(property="course"), state=StartForm.course)
async def cq_start_choose_course(query: types.CallbackQuery, state: FSMContext, callback_data: dict):
    logger.info(
        "User {user} changed course to {course}",
        user=query.from_user.id,
        course=callback_data["value"]
    )

    await state.update_data(course=callback_data["value"])
    data = await state.get_data()
    await state.set_state(StartForm.group)
    markup = await start.start_kb_choose_group(data["faculty"], int(callback_data["value"]))
    await query.message.edit_text("Выберите группу", reply_markup=markup)


@dp.callback_query_handler(start.cb_user_start.filter(property="group"), state=StartForm.group)
async def cq_start_choose_group(query: types.CallbackQuery, state: FSMContext, callback_data: dict):
    logger.info(
        "User {user} changed group to {group}",
        user=query.from_user.id,
        group=callback_data["value"]
    )
    data = await state.get_data()
    await UserModel.update_or_create(defaults={"group_id": callback_data["value"],
                                               "type": int(data["user_type"]),
                                               },
                                     id=query.from_user.id)
    await state.finish()
    await query.message.delete()
    await bot.send_message(query.from_user.id, start.start_completed, reply_markup=commands_kb)


@dp.callback_query_handler(start.cb_user_start.filter(property="department"), state=StartForm.department)
async def cq_start_choose_department(query: types.CallbackQuery, state: FSMContext, callback_data: dict):
    logger.info(
        "User {user} changed department {department}",
        user=query.from_user.id,
        department=callback_data["value"]
    )
    await state.update_data(department=callback_data["value"])
    await state.set_state(StartForm.employee)
    markup = await start.start_kb_choose_employee(int(callback_data["value"]))
    await query.message.edit_text("Найдите себя", reply_markup=markup)


@dp.callback_query_handler(start.cb_user_start.filter(property="employee"), state=StartForm.employee)
async def cq_start_choose_employee(query: types.CallbackQuery, state: FSMContext, callback_data: dict):
    logger.info(
        "User {user} changed employee to {employee}",
        user=query.from_user.id,
        employee=callback_data["value"]
    )
    data = await state.get_data()
    await UserModel.update_or_create(defaults={"employee_id": callback_data["value"],
                                               "type": int(data["user_type"]),
                                               },
                                     id=query.from_user.id)
    await state.finish()
    await query.message.delete()
    await bot.send_message(query.from_user.id, start.start_completed, reply_markup=commands_kb)


@dp.message_handler(commands=["version"])
async def cmd_version(message: types.Message):
    await message.reply("My Engine:\n{aiogram}".format(aiogram=quote_html(str(aiogram_core.SysInfo()))))


@dp.errors_handler()
async def errors_handler(update: types.Update, exception: Exception):
    try:
        raise exception
    except Exception as e:
        logger.exception("Cause exception {e} in update {update}", e=e, update=update)
    return True
