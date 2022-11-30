from aiogram.dispatcher.filters.state import StatesGroup, State


__all__ = ("Register",)


class Register(StatesGroup):
    faculty = State()
    course = State()
    group = State()
