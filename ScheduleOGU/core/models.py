import datetime

from tortoise import fields
from tortoise.models import Model

from ScheduleOGU.core.enums import DayType

__all__ = (
    "ScheduleSubjectModel",
    "EmployeeModel")


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

    @property
    def datetime(self):
        return datetime.datetime.fromtimestamp(self.date).strftime("%d.%m.%Y")

    def __str__(self):
        name = self.name
        if len(self.name) > 15:
            name = name[::-1]
            x = name.find(' ', -30, -1)
            x = -x
            name = name[::-1]
            name = name[0:x] + '\n' + name[x:]
        return f"""{name} \n({self.type}) \n{self.employee.short_full_name} \n{self.building}-{self.audience}\n\u200b\n"""
