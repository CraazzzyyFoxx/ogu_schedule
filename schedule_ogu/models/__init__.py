import datetime

import attr

from schedule_ogu.models.enums import DayType
from schedule_ogu.models.db import ScheduleSubjectModel


__all__ = ("ScheduleDay",
           )


@attr.define(kw_only=True)
class ScheduleDay:
    day: DayType
    date: datetime.datetime
    subjects: list[ScheduleSubjectModel]
