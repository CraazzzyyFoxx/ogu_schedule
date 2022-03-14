import math
import typing as t

from datetime import datetime

from aiogram.utils.markdown import escape_md
from tabulate import tabulate

from ..core.enums import DayType, days_ru
from ..core.models import ScheduleDayModel

__all__ = ("ScheduleTime",
           "print_schedule",
           "format_buttons")


class ScheduleTime:
    step = 604800
    start_semester = int(datetime(2022, 2, 7).timestamp())

    @classmethod
    def compute_week(cls):
        timestamp = datetime.utcnow().timestamp() - cls.start_semester
        return math.ceil(timestamp / cls.step)

    @classmethod
    def compute_timestamp_for_site(cls, week: int = None):
        # Thanks oreluniver.ru
        return str(cls.compute_timestamp(week)) + "000"

    @classmethod
    def compute_timestamp(cls, week: int = None):
        week_raw = week or cls.compute_week()
        if datetime.utcnow().weekday() != 6:
            week_raw -= 1
        return cls.start_semester + cls.step * week_raw

    @classmethod
    def compute_day(cls, week: int, day: DayType):
        timestamp = cls.compute_timestamp(week)
        return datetime.fromtimestamp(timestamp + (day.value - 1) * 86400).strftime("%d.%m.%Y")


class print_schedule:
    def __init__(self, schedule: t.List[ScheduleDayModel], day: DayType, week: int = ScheduleTime.compute_week()):
        self.header = days_ru[day] + f" ({ScheduleTime.compute_day(week, day)})"
        self.str_subjects: t.Dict[int, str] = dict()

        for day_ in schedule:
            if day_.day == day:
                number = 1
                for subject in day_.subjects:
                    if number != subject.number:
                        self.str_subjects[number] = "<b>Окно</b>"
                        number += 1

                    if self.str_subjects.get(subject.number) is not None:
                        self.str_subjects[subject.number] += "\n <b>Подгруппа 1</b> \n"
                        self.str_subjects[subject.number] += subject.__str__()
                        self.str_subjects[subject.number] += "\n <b>Подгруппа 2</b> "
                    else:
                        self.str_subjects[subject.number] = subject.__str__()

                    number += 1

    def __str__(self):
        if not self.str_subjects:
            return tabulate([["Спи спокойно, \n в этот день нет пар"]], headers=[self.header], tablefmt="simple")
        rows = [[subject + "\n\u200b\n"] for subject in self.str_subjects.values()]
        table = tabulate(rows, headers=[self.header], tablefmt="simple")
        return table


def format_buttons(buttons, row_width=3):
    keyboard = []
    row = []
    for index, button in enumerate(buttons, start=1):
        row.append(button)
        if index % row_width == 0:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    return keyboard
