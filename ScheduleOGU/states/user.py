from aiogram.dispatcher.filters.state import StatesGroup, State


__all__ = ("Register", "Test")


class Register(StatesGroup):
    faculty = State()
    course = State()
    group = State()


class Test(StatesGroup):
    Q1 = State()
    Q2 = State()
