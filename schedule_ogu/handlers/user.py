from aiogram.dispatcher import FSMContext
from aiogram import types

from schedule_ogu.services.schedule import ScheduleService
from schedule_ogu import Years, UserModel, format_buttons, UserType
from schedule_ogu.states import Register
from schedule_ogu.misc import dp


# @dp.message_handler(commands=['start'])
# async def choose_group(message: types.Message):
#     faculties = await ScheduleService.get_faculty_views()
#     mk = types.ReplyKeyboardMarkup(
#         keyboard=format_buttons([types.KeyboardButton(faculty.short_title) for faculty in faculties], row_width=4),
#         resize_keyboard=True,
#         one_time_keyboard=True,
#         selective=True
#     )
#
#     await message.reply("Выбери факультет", reply_markup=mk)
#     await Register.faculty.set()
#
#
# @dp.message_handler(state=Register.faculty)
# async def answer_faculty(message: types.Message, state: FSMContext):
#     faculties = await ScheduleService.get_faculty_views()
#     if message.text in [faculty.short_title for faculty in faculties]:
#         for faculty in faculties:
#             if faculty.short_title == message.text:
#                 buttons = [types.KeyboardButton(value_.value) for name, value_ in Years._member_map_.items()]
#                 mk = types.ReplyKeyboardMarkup(keyboard=[buttons],
#                                                resize_keyboard=True,
#                                                one_time_keyboard=True,
#                                                selective=True
#                                                )
#                 await message.reply("Выбери курс", reply_markup=mk)
#                 await state.update_data(faculty=faculty)
#                 await Register.course.set()
#     else:
#         await Register.faculty.set()
#
#
# @dp.message_handler(state=Register.course)
# async def answer_course(message: types.Message, state: FSMContext):
#     faculties = await ScheduleService.get_faculty_views()
#     if message.text in [str(value_.value) for name, value_ in Years._member_map_.items()]:
#         data = await state.get_data()
#         faculty_ = data.get("faculty")
#         for faculty in faculties:
#             if faculty == faculty_:
#                 buttons = [types.KeyboardButton(group.name) for group in faculty.groups if group.course == int(message.text)]
#                 if len(buttons) == 0:
#                     return await Register.course.set()
#                 mk = types.ReplyKeyboardMarkup(keyboard=format_buttons(buttons, row_width=6),
#                                                resize_keyboard=True,
#                                                one_time_keyboard=True,
#                                                selective=True
#                                                )
#                 await state.update_data(course=message.text)
#                 await message.answer("Выбери группу", reply_markup=mk)
#                 await Register.group.set()
#
#     else:
#         await Register.course.set()
#
#
# @dp.message_handler(state=Register.group)
# async def answer_group(message: types.Message, state: FSMContext):
#     faculties = await ScheduleService.get_faculty_views()
#     if message.text in [group.name for faculty in faculties for group in faculty.groups]:
#         for group in [group for faculty in faculties for group in faculty.groups]:
#             if group.name == message.text:
#                 await UserModel.update_or_create(defaults={"group_id": group.id},
#                                                  id=message.from_user.id,
#                                                  type=UserType.Student)
#                 await message.answer("Спасибо, что пользуетесь ботом.", reply_markup=types.ReplyKeyboardRemove())
#                 await state.finish()
#
#     else:
#         await Register.group.set()
