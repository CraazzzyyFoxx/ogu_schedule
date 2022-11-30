import datetime
import typing

from tortoise import fields
from tortoise.models import Model

from schedule_ogu.utils.enums import DayType, EducationalLevel, Years, SubjectType, ActionStats, UserType

__all__: typing.Sequence[str] = (
    "ScheduleSubjectModel",
    "EmployeeModel",
    "FacultyModel",
    "GroupModel",
    "UserModel",
    "StatsModel",
    "CookieModel",
    "UserAgentModel",
    "DepartmentModel",
    "ExamModel",)


class StatsModel(Model):
    id = fields.IntField(pk=True)
    action = fields.IntEnumField(ActionStats)
    datetime = fields.DatetimeField(auto_now_add=True)
    extra = fields.TextField(null=True)

    class Meta:
        """Metaclass to set table name and description"""

        table = "stats"
        table_description = "Stores information about the stats"


class UserModel(Model):
    id = fields.BigIntField(pk=True, generated=False)
    group_id = fields.IntField(null=True)
    employee_id = fields.IntField(null=True)
    type = fields.IntEnumField(UserType, default=UserType.Student)
    is_superuser = fields.BooleanField(default=False)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        """Metaclass to set table name and description"""

        table = "user"
        table_description = "Stores information about the user"


class CookieModel(Model):
    id = fields.BigIntField(pk=True)
    datetime = fields.DatetimeField(auto_now_add=True)
    extra = fields.TextField()

    class Meta:
        """Metaclass to set table name and description"""

        table = "cookie"
        table_description = "Stores information about the cookies"


class UserAgentModel(Model):
    id = fields.BigIntField(pk=True)
    datetime = fields.DatetimeField(auto_now_add=True)
    extra = fields.TextField()

    class Meta:
        """Metaclass to set table name and description"""

        table = "user_agent"
        table_description = "Stores information about the user_agent"


class FacultyModel(Model):
    id = fields.IntField(pk=True, generated=False)
    title = fields.TextField()
    short_title = fields.TextField()

    groups: fields.ReverseRelation["GroupModel"]
    departments: fields.ReverseRelation["DepartmentModel"]

    class Meta:
        """Metaclass to set table name and description"""

        table = "faculty"
        table_description = "Stores information about the faculty"


class DepartmentModel(Model):
    id = fields.IntField(pk=True, generated=False)
    title = fields.TextField()
    short_title = fields.TextField()

    employees: fields.ReverseRelation["EmployeeModel"]
    faculty: fields.ForeignKeyRelation["FacultyModel"] = fields.ForeignKeyField(model_name='main.FacultyModel',
                                                                                related_name='departments',
                                                                                to_field='id')

    class Meta:
        """Metaclass to set table name and description"""

        table = "department"
        table_description = "Stores information about the department"


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
    exams: fields.ReverseRelation['ExamModel']
    department: fields.ForeignKeyRelation["DepartmentModel"] = fields.ForeignKeyField(model_name='main.DepartmentModel',
                                                                                      related_name='employees',
                                                                                      to_field='id')

    class Meta:
        """Metaclass to set table name and description"""

        table = "employee"
        table_description = "Stores information about the employee"

    @property
    def short_full_name(self):
        return f'{self.second_name} {self.name[0]}.{self.middle_name[0]}.'

    @property
    def url(self):
        return f"https://oreluniver.ru/employee/{self.id}"


class ScheduleSubjectModel(Model):
    id = fields.IntField(pk=True)
    day = fields.IntEnumField(DayType)
    date = fields.IntField()

    name = fields.TextField()
    sub_group = fields.IntField()
    audience = fields.TextField()
    building = fields.SmallIntField()
    number = fields.SmallIntField()
    type = fields.IntEnumField(SubjectType)

    zoom_link = fields.TextField(null=True)
    zoom_password = fields.TextField(null=True)

    employee: fields.ForeignKeyRelation[EmployeeModel] = fields.ForeignKeyField(model_name='main.EmployeeModel',
                                                                                related_name='subjects',
                                                                                to_field='id')
    group: fields.ForeignKeyRelation[GroupModel] = fields.ForeignKeyField(model_name='main.GroupModel',
                                                                          to_field='id')

    class Meta:
        """Metaclass to set table name and description"""

        table = "subject"
        table_description = "Stores information about the subject"

    @property
    def str_date(self):
        return datetime.datetime.fromtimestamp(self.date).strftime("%d.%m.%Y")  # type: ignore


class ExamModel(Model):
    id = fields.IntField(pk=True)
    day = fields.IntEnumField(DayType)
    date = fields.IntField()

    name = fields.TextField()
    sub_group = fields.IntField()
    dislocation = fields.TextField()
    number = fields.SmallIntField()
    type = fields.IntEnumField(SubjectType)
    time = fields.TextField()

    zoom_link = fields.TextField(null=True)
    zoom_password = fields.TextField(null=True)

    employee: fields.ForeignKeyRelation[EmployeeModel] = fields.ForeignKeyField(model_name='main.EmployeeModel',
                                                                                related_name='exams',
                                                                                to_field='id')
    group: fields.ForeignKeyRelation[GroupModel] = fields.ForeignKeyField(model_name='main.GroupModel',
                                                                          to_field='id')

    class Meta:
        """Metaclass to set table name and description"""

        table = "exams"
        table_description = "Stores information about the exam"

    @property
    def str_date(self):
        return datetime.datetime.fromtimestamp(self.date).strftime("%d.%m.%Y")  # type: ignore
