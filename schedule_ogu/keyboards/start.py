from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

from schedule_ogu import FacultyModel, DepartmentModel, GroupModel, UserType, Years, EmployeeModel, format_buttons

start_completed = """
✅Группа выбрана, можешь пользоваться расписанием
⚙️Команды бота
/start - перезапустить бота (изменить группу)
/today - расписание на сегодня
/next - расписание на завтра
/select - выбрать дату
"""

cb_user_start = CallbackData("user", "property", "value")

start_kb_choose_user_type = InlineKeyboardMarkup(row_width=2)
inline_user_type_student = InlineKeyboardButton('Студент',
                                                callback_data=cb_user_start.new(property="user_type",
                                                                                value=UserType.Student.value))
inline_user_type_lecturer = InlineKeyboardButton('Преподаватель ',
                                                 callback_data=cb_user_start.new(property="user_type",
                                                                                 value=UserType.Lecturer.value))
start_kb_choose_user_type.add(inline_user_type_student, inline_user_type_lecturer)

course_buttons = (
    InlineKeyboardButton(f"{Years.First}", callback_data=cb_user_start.new(property="course",
                                                                           value=Years.First.value)),
    InlineKeyboardButton(f"{Years.Second}", callback_data=cb_user_start.new(property="course",
                                                                            value=Years.Second.value)),
    InlineKeyboardButton(f"{Years.Third}", callback_data=cb_user_start.new(property="course",
                                                                           value=Years.Third.value)),
    InlineKeyboardButton(f"{Years.Fourth}", callback_data=cb_user_start.new(property="course",
                                                                            value=Years.Fourth.value)),
    InlineKeyboardButton(f"{Years.Fifth}", callback_data=cb_user_start.new(property="course",
                                                                           value=Years.Fifth.value)))


async def start_kb_choose_faculty() -> InlineKeyboardMarkup:
    faculties = await FacultyModel.all()
    buttons = [InlineKeyboardButton(faculty.short_title,
                                    callback_data=cb_user_start.new(property="faculty", value=faculty.id))
               for faculty in faculties]

    return InlineKeyboardMarkup(inline_keyboard=format_buttons(buttons, row_width=3), row_width=5)


async def start_kb_choose_course() -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(row_width=5)
    kb.row(*course_buttons)
    return kb


async def start_kb_choose_department(faculty_id: int) -> InlineKeyboardMarkup:
    departments = await DepartmentModel.filter(faculty_id=faculty_id)
    buttons = [InlineKeyboardButton(department.short_title,
                                    callback_data=cb_user_start.new(property="department",
                                                                    value=department.id))
               for department in departments]

    return InlineKeyboardMarkup(inline_keyboard=format_buttons(buttons, row_width=3), row_width=5)


async def start_kb_choose_group(faculty_id: int, course: int) -> InlineKeyboardMarkup:
    groups = await GroupModel.filter(faculty_id=faculty_id, course=course)
    buttons = [InlineKeyboardButton(group.name,
                                    callback_data=cb_user_start.new(property="group", value=group.id))
               for group in groups
               ]

    return InlineKeyboardMarkup(inline_keyboard=format_buttons(buttons, row_width=3), row_width=5)


async def start_kb_choose_employee(department_id: int) -> InlineKeyboardMarkup:
    employees = await EmployeeModel.filter(department_id=department_id)
    buttons = [InlineKeyboardButton(employee.short_full_name,
                                    callback_data=cb_user_start.new(property="employee", value=employee.id))
               for employee in employees]

    return InlineKeyboardMarkup(inline_keyboard=format_buttons(buttons, row_width=3), row_width=5)
