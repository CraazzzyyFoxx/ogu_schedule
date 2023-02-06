from aiogram import types, Router, F
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.filters.state import StatesGroup, State
from aiogram.types.error_event import ErrorEvent
from aiogram.utils.markdown import hbold, hlink
from loguru import logger

from schedule_ogu.keyboards import start
from schedule_ogu.keyboards.commands import commands_kb
from schedule_ogu.models.db import UserModel
from schedule_ogu.models.enums import UserType

router = Router()


class StartForm(StatesGroup):
    user_type = State()
    faculty = State()
    department = State()
    group = State()
    course = State()
    employee = State()


@router.message(F.chat.type == "private", CommandStart())
async def cmd_start(message: types.Message, state: FSMContext):
    logger.info("User {user} start conversation with bot", user=message.from_user.id)
    await message.answer(
        f"Привет, {hbold(message.from_user.full_name)}.\n"
        f"Отправь /help если ты хочешь увидеть список команд\n"
        f"Мой исходный код: {hlink('GitHub', 'https://github.com/CraazzzyyFoxx/ogu_schedule')} \n"

    )
    await state.set_state(StartForm.user_type)
    await message.answer("Студент или Преподаватель?", reply_markup=start.start_kb_choose_user_type())


@router.message(F.chat.type == "group", Command(commands=["start"]))
async def cmd_start(message: types.Message):
    await message.answer(
        f"Привет, {hbold(message.from_user.full_name)}.\n"
        f"Отправь /help если ты хочешь увидеть список команд\n"
        f"Мой исходный код: {hlink('GitHub', 'https://github.com/CraazzzyyFoxx/ogu_schedule')} \n\n"
        f"{hbold('Регистрация доступна только в лс')}"

    )


@router.message(Command(commands=["help"]))
async def cmd_help(message: types.Message):
    logger.info("User {user} read help in {chat}", user=message.from_user.id, chat=message.chat.id)
    text = [
        hbold("Здесь ты можешь увидить список моих команд:"),
        "{command} - Получите это сообщение".format(command="/help"),
        "{command} - My version".format(command="/version"),
        "",
    ]

    if message.chat.type == "private":
        text.extend([hbold("Доступно только в лс:"),
                     "{command} - Начните разговор с ботом".format(command="/start"),
                     "",
                     ])
    await message.reply("\n".join(text))


@router.callback_query(start.UserStartCallback.filter(F.action == "user_type"), StartForm.user_type)
async def cq_start_choose_user_type(
        callback: types.CallbackQuery,
        callback_data: start.UserStartCallback,
        state: FSMContext
):
    logger.info(
        "User {user} changed user_type to {user_type}",
        user=callback.from_user.id,
        user_type=callback_data.value
    )
    await state.update_data(user_type=callback_data.value)
    await state.set_state(StartForm.faculty)
    markup = await start.start_kb_choose_faculty()
    await callback.message.edit_text("Выберите факультет", reply_markup=markup)


@router.callback_query(start.UserStartCallback.filter(F.action == "faculty"), StartForm.faculty)
async def cq_start_choose_faculty(
        callback: types.CallbackQuery,
        callback_data: start.UserStartCallback,
        state: FSMContext
):
    logger.info(
        "User {user} changed  faculty to {faculty_id}",
        user=callback.from_user.id,
        faculty_id=callback_data.value
    )
    await state.update_data(faculty=callback_data.value)
    data = await state.get_data()
    if int(data["user_type"]) is UserType.Student.value:
        await state.set_state(StartForm.course)
        markup = start.start_kb_choose_course()
        await callback.message.edit_text("Выберите курс", reply_markup=markup)
    else:
        await state.set_state(StartForm.department)
        markup = await start.start_kb_choose_department(int(callback_data.value))
        await callback.message.edit_text("Выберите кафедру", reply_markup=markup)


@router.callback_query(start.UserStartCallback.filter(F.action == "course"), StartForm.course)
async def cq_start_choose_course(
        callback: types.CallbackQuery,
        callback_data: start.UserStartCallback,
        state: FSMContext
):
    logger.info(
        "User {user} changed course to {course}",
        user=callback.from_user.id,
        course=callback_data.value
    )

    await state.update_data(course=callback_data.value)
    data = await state.get_data()
    await state.set_state(StartForm.group)
    markup = await start.start_kb_choose_group(data["faculty"], int(callback_data.value))
    await callback.message.edit_text("Выберите группу", reply_markup=markup)


@router.callback_query(start.UserStartCallback.filter(F.action == "group"), StartForm.group)
async def cq_start_choose_group(
        callback: types.CallbackQuery,
        callback_data: start.UserStartCallback,
        state: FSMContext
):
    logger.info(
        "User {user} changed group to {group}",
        user=callback.from_user.id,
        group=callback_data.value
    )
    data = await state.get_data()
    await UserModel.update_or_create(defaults={"group_id": callback_data.value,
                                               "type": int(data["user_type"]),
                                               },
                                     id=callback.from_user.id)
    await state.clear()
    await callback.message.delete()
    await callback.message.answer(start.start_completed, reply_markup=commands_kb)


@router.callback_query(start.UserStartCallback.filter(F.action == "department"), StartForm.department)
async def cq_start_choose_department(
        callback: types.CallbackQuery,
        callback_data: start.UserStartCallback,
        state: FSMContext
):
    logger.info(
        "User {user} changed department {department}",
        user=callback.from_user.id,
        department=callback_data.value
    )
    await state.update_data(department=callback_data.value)
    await state.set_state(StartForm.employee)
    markup = await start.start_kb_choose_employee(int(callback_data.value))
    await callback.message.edit_text("Найдите себя", reply_markup=markup)


@router.callback_query(start.UserStartCallback.filter(F.action == "employee"), StartForm.employee)
async def cq_start_choose_employee(
        callback: types.CallbackQuery,
        callback_data: start.UserStartCallback,
        state: FSMContext
):
    logger.info(
        "User {user} changed employee to {employee}",
        user=callback.from_user.id,
        employee=callback_data.value
    )
    data = await state.get_data()
    await UserModel.update_or_create(defaults={"employee_id": callback_data.value,
                                               "type": int(data["user_type"]),
                                               },
                                     id=callback.from_user.id)
    await state.clear()
    await callback.message.delete()
    await callback.message.answer(start.start_completed, reply_markup=commands_kb)


@router.errors()
async def error_handler(exception: ErrorEvent):
    try:
        raise exception.exception
    except Exception as e:
        logger.exception("Cause exception {e} in update {update}", e=e, update=exception.update)
    return True
