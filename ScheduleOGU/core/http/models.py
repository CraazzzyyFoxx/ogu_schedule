import typing as t
from datetime import datetime

from pydantic import Field, BaseModel, validator

from ..enums import try_value, DayType, EducationalLevel, educational_level_ru


class ScheduleEntryHTTP(BaseModel):
    name: str = Field(alias="TitleSubject")
    type: str = Field(alias="TypeLesson")

    date: int = Field(alias="DateLesson")
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
        return (datetime.strptime(
            value,
            "%Y-%m-%d"
        )
                .timestamp())

    @validator("day_week", pre=True)
    def parse_day_week(cls, value):
        return try_value(DayType, value)


class ScheduleDayHTTP:
    def __init__(self, day: DayType, entries: t.List[ScheduleEntryHTTP]):
        self.day = day
        self.date = entries[0].date
        self.subjects = list()
        self.subjects.extend(entries)


class ScheduleHTTP:
    def __init__(self, entries: t.List[ScheduleEntryHTTP]):
        self.group_id = entries[0].group_id
        self.days = dict()

        for entry in entries:
            day = try_value(DayType, entry.day_week)
            if day not in self.days.keys():
                self.days[day] = ScheduleDayHTTP(day, [entry])
            else:
                self.days[day].subjects.append(entry)


class StudentGroupHTTP(BaseModel):
    id: int = Field(alias='idgruop')
    direction: str = Field(alias="Codedirection")
    level: EducationalLevel = Field(alias="levelEducation")
    name: str = Field(alias="title")

    @validator("level", pre=True)
    def parse_level(cls, value):
        return educational_level_ru.get(value)


class FacultyHTTP(BaseModel):
    id: int = Field(alias="idDivision")
    title: str = Field(alias="titleDivision")
    short_title: str = Field(alias="shortTitle")

    def __hash__(self):
        return self.id
