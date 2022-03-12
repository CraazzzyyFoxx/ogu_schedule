import typing as t
from datetime import datetime

from pydantic import Field, BaseModel, validator

from ..enums import try_value, DayType


class ScheduleEntryHTTP(BaseModel):
    name: str = Field(alias="TitleSubject")
    type: str = Field(alias="TypeLesson")

    date: datetime = Field(alias="DateLesson")
    day_week: int = Field(alias="DayWeek")

    building: str = Field(alias='Korpus')
    audience: str = Field(alias="NumberRoom")
    number: int = Field(alias="NumberLesson")

    employee_id: int
    employee_name: str = Field(alias="Name")
    employee_second_name: str = Field(alias="Family")
    employee_middle_name: str = Field(alias='SecondName')

    group_id: int = Field(alias="idGruop")

    zoom_link: t.Optional[str]
    zoom_password: t.Optional[str]

    @validator("date", pre=True)
    def parse_date(cls, value):
        return datetime.strptime(
            value,
            "%Y-%m-%d"
        )

    @validator("day_week", pre=True)
    def parse_day_week(cls, value):
        return try_value(DayType, value)