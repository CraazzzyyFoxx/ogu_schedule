import typing as t
from datetime import datetime

from tortoise import fields
from tortoise.models import Model
from pydantic import Field, BaseModel, validator

from ScheduleOGU.core.enums import DayType, try_value

__all__ = (
    "ScheduleSubjectModel",
    "EmployeeModel",
    "ScheduleEntryHTTP",)


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


class EmployeeModel(Model):
    id = fields.IntField(pk=True, generated=False)
    name = fields.TextField()
    second_name = fields.TextField()
    middle_name = fields.TextField()

    subjects: fields.ReverseRelation['ScheduleSubjectModel']

    class Meta:
        """Metaclass to set table name and description"""

        table = "employee"
        table_description = "Stores information about the employee"

    @property
    def short_full_name(self):
        return f'{self.second_name} {self.name[0]}.{self.middle_name[0]}.'


class ScheduleSubjectModel(Model):
    id = fields.IntField(pk=True)
    name = fields.TextField()
    audience = fields.TextField()
    building = fields.SmallIntField()
    number = fields.SmallIntField()
    type = fields.TextField()

    date = fields.IntField()
    day = fields.IntEnumField(DayType)
    group_id = fields.IntField()

    zoom_link = fields.TextField(null=True)
    zoom_password = fields.TextField(null=True)

    employee: fields.ForeignKeyRelation[EmployeeModel] = fields.ForeignKeyField(model_name='main.EmployeeModel',
                                                                                related_name='subjects',
                                                                                to_field='id')

    class Meta:
        """Metaclass to set table name and description"""

        table = "subject"
        table_description = "Stores information about the subject"
        unique_together = ("number", "name", "date")

    def __str__(self):
        name = self.name
        if len(self.name) > 15:
            name = name[::-1]
            x = name.find(' ', -30, -1)
            x = -x
            name = name[::-1]
            name = name[0:x] + '\n' + name[x:]
        return f"""{name} \n({self.type}) \n{self.employee.short_full_name} \n{self.building}-{self.audience}\n\u200b\n"""
