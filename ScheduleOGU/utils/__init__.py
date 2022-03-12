import math
from datetime import datetime

from tabulate import tabulate

from ..core.enums import DayType

__all__ = ("days_ru",
           "ScheduleTime",
           "print_schedule")


days_ru = {DayType.Monday: "Понедельник",
           DayType.Tuesday: "Вторник",
           DayType.Wednesday: "Среда",
           DayType.Thursday: "Четверг",
           DayType.Friday: "Пятница",
           DayType.Saturday: "Суббота",
           }


class ScheduleTime:
    step = 604800
    start_semester = int(datetime(2022, 2, 7).timestamp())

    @classmethod
    def compute_week(cls):
        timestamp = datetime.utcnow().timestamp() - cls.start_semester
        return math.ceil(timestamp / cls.step)

    @classmethod
    def compute_timestamp_for_site(cls, week: int = None):
        if week is not None:
            raw = cls.start_semester + cls.step * (week - 1)
        else:
            raw = cls.start_semester + cls.step * (cls.compute_week() - 1)
        return str(raw) + "000"

    @classmethod
    def compute_timestamp(cls, week: int = None):
        if week is not None:
            raw = cls.start_semester + cls.step * (week - 1)
        else:
            raw = cls.start_semester + cls.step * (cls.compute_week() - 1)
        return raw

    @classmethod
    def compute_day(cls, week: int, day: DayType):
        timestamp = cls.compute_timestamp(week)
        return datetime.fromtimestamp(timestamp + (day.value - 1) * 86400).strftime("%d.%m.%Y")


def print_schedule(schedule, day: DayType, week: int = ScheduleTime.compute_week()):
    header = days_ru[day] + f" ({ScheduleTime.compute_day(week, day)})"
    if not schedule.get(day):
        return tabulate([["Спи спокойно, \n в этот день нет пар"]], headers=[header], tablefmt="simple")
    rows = [[subject] for subject in schedule[day]]
    return tabulate(rows, headers=[header], tablefmt="simple")
