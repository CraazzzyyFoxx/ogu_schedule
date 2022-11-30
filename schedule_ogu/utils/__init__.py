from datetime import datetime, timedelta

from schedule_ogu.utils.enums import DayType

__all__ = ("ScheduleTime",
           "format_buttons")


class ScheduleTime:
    time_week = 604800
    start_semester = int(datetime(2022, 8, 29).timestamp())

    @classmethod
    def compute_current_week(cls) -> int:
        return int((cls._compute_timestamp() - cls.start_semester) / cls.time_week) + 1

    @classmethod
    def compute_timestamp_for_site(cls, week: int = None) -> str:
        # Thanks oreluniver.ru
        return f"{cls._compute_timestamp(week=week)}000"

    @classmethod
    def _compute_timestamp(cls, week: int = None) -> int:
        t = datetime.utcnow()
        time = int(datetime(t.year, t.month, t.day).timestamp())
        if week:
            return time + (week - cls.compute_current_week()) * cls.time_week
        return time

    @classmethod
    def compute_timestamp(cls, *, week_delta: int = 0, day: DayType = 0, past: bool = False) -> int:
        t = datetime.utcnow()
        time = int(datetime(t.year, t.month, t.day).timestamp())

        weekday = t.weekday()
        delta = 0

        if past:
            week_delta -= 1

        if day != 0:
            if weekday < day:
                delta = timedelta(days=day - weekday).total_seconds()
            elif weekday > day:
                delta = (timedelta(days=day - weekday) + timedelta(days=7)).total_seconds()

        return time + delta + week_delta * cls.time_week

    @classmethod
    def today(cls) -> DayType:
        day = datetime.utcnow().weekday()
        if day == 6:
            return DayType.Monday
        return DayType(day)

    @classmethod
    def next_day(cls) -> DayType:
        day = datetime.utcnow().weekday()
        if day == 5 or day == 6:
            return DayType.Monday

        return DayType(day + 1)

    @classmethod
    def previous_day(cls) -> DayType:
        day = datetime.utcnow().weekday()
        if day == 0 or day == 6:
            return DayType.Saturday

        return DayType(day - 1)


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
