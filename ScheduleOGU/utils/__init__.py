import math
from datetime import datetime

from ..core.enums import DayType
from .http import *

__all__ = ("days_ru",
           "ScheduleTime",
           "flatten_error_dict",
           "json_or_text")


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
