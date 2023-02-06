from aiogram.types import InlineKeyboardMarkup
from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import InlineKeyboardBuilder

from schedule_ogu.models.db import FacultyModel, DepartmentModel, GroupModel, EmployeeModel
from schedule_ogu.models.enums import Years, UserType

start_completed = """
✅Регистрация завершена, можешь пользоваться расписанием
⚙️Команды бота
/start - перезапустить бота (изменить группу)
/today - расписание на сегодня
/next - расписание на завтра
"""


class UserStartCallback(CallbackData, prefix="start"):
    action: str
    value: int | None


def start_kb_choose_user_type() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text='Студент', callback_data=UserStartCallback(action="user_type", value=UserType.Student))
    builder.button(text='Преподаватель ', callback_data=UserStartCallback(action="user_type", value=UserType.Lecturer))
    return builder.as_markup()


async def start_kb_choose_faculty() -> InlineKeyboardMarkup:
    faculties = await FacultyModel.all()
    builder = InlineKeyboardBuilder()

    for faculty in faculties:
        builder.button(text=faculty.short_title, callback_data=UserStartCallback(action="faculty", value=faculty.id))
    builder.adjust(5)
    return builder.as_markup()


def start_kb_choose_course() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for year in Years:
        builder.button(text=f"{year}", callback_data=UserStartCallback(action="course", value=year))
    return builder.as_markup()


async def start_kb_choose_department(faculty_id: int) -> InlineKeyboardMarkup:
    departments = await DepartmentModel.filter(faculty_id=faculty_id)
    builder = InlineKeyboardBuilder()
    for department in departments:
        builder.button(text=department.short_title, callback_data=UserStartCallback(action="department",
                                                                                    value=department.id))
    builder.adjust(5)
    return builder.as_markup()


async def start_kb_choose_group(faculty_id: int, course: int) -> InlineKeyboardMarkup:
    groups = await GroupModel.filter(faculty_id=faculty_id, course=course)
    builder = InlineKeyboardBuilder()
    for group in groups:
        builder.button(text=group.name, callback_data=UserStartCallback(action="group", value=group.id))

    builder.adjust(5)
    return builder.as_markup()


async def start_kb_choose_employee(department_id: int) -> InlineKeyboardMarkup:
    employees = await EmployeeModel.filter(department_id=department_id)
    builder = InlineKeyboardBuilder()
    for employee in employees:
        builder.button(text=employee.short_full_name, callback_data=UserStartCallback(action="employee",
                                                                                      value=employee.id))

    builder.adjust(5)
    return builder.as_markup()
