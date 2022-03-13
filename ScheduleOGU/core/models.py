import datetime

from tortoise import fields
from tortoise.models import Model

from ScheduleOGU.core.enums import DayType, EducationalLevel, Years, times

__all__ = (
    "ScheduleSubjectModel",
    "EmployeeModel",
    "FacultyModel",
    "GroupModel",
    "UserModel",
    "ScheduleDayModel")


class UserModel(Model):
    id = fields.BigIntField(pk=True, generated=False)
    group_id = fields.IntField()

    class Meta:
        """Metaclass to set table name and description"""

        table = "user"
        table_description = "Stores information about the user"


class FacultyModel(Model):
    id = fields.IntField(pk=True, generated=False)
    title = fields.TextField()
    short_title = fields.TextField()

    groups: fields.ReverseRelation["GroupModel"]

    class Meta:
        """Metaclass to set table name and description"""

        table = "faculty"
        table_description = "Stores information about the faculty"


class GroupModel(Model):
    id = fields.IntField(pk=True, generated=False)
    direction = fields.TextField()
    course = fields.IntEnumField(Years)
    level = fields.IntEnumField(EducationalLevel)
    name = fields.TextField()

    faculty: fields.ForeignKeyRelation["FacultyModel"] = fields.ForeignKeyField(model_name='main.FacultyModel',
                                                                                related_name='groups',
                                                                                to_field='id')

    class Meta:
        """Metaclass to set table name and description"""

        table = "group"
        table_description = "Stores information about the group"


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

    @property
    def url(self):
        return f"<a href='http://oreluniver.ru/employee/{self.id}'>{self.short_full_name}</a>"


class ScheduleDayModel(Model):
    id = fields.IntField(pk=True)
    day = fields.IntEnumField(DayType)
    date = fields.IntField()
    group_id = fields.IntField()

    subjects: fields.ReverseRelation["ScheduleSubjectModel"]

    class Meta:
        """Metaclass to set table name and description"""

        table = "day"
        table_description = "Stores information about the day"


class ScheduleSubjectModel(Model):
    id = fields.IntField(pk=True)
    day: fields.ForeignKeyRelation[ScheduleDayModel] = fields.ForeignKeyField(model_name='main.ScheduleDayModel',
                                                                              related_name='subjects',
                                                                              to_field='id')

    name = fields.TextField()
    audience = fields.TextField()
    building = fields.SmallIntField()
    number = fields.SmallIntField()
    type = fields.TextField()

    zoom_link = fields.TextField(null=True)
    zoom_password = fields.TextField(null=True)

    employee: fields.ForeignKeyRelation[EmployeeModel] = fields.ForeignKeyField(model_name='main.EmployeeModel',
                                                                                related_name='subjects',
                                                                                to_field='id')

    class Meta:
        """Metaclass to set table name and description"""

        table = "subject"
        table_description = "Stores information about the subject"

    @property
    def datetime(self):
        return datetime.datetime.fromtimestamp(self.date).strftime("%d.%m.%Y")  # type: ignore

    def __str__(self):
        name = self.name
        if len(self.name) > 15:
            name = name[::-1]
            x = name.find(' ', -30, -1)
            x = -x
            name = name[::-1]
            name = name[0:x] + '\n' + name[x:]
        return f"{name}\n({self.type})\n🕐{times[self.number]}\n{self.employee.url}\n{self.building}-{self.audience}"
