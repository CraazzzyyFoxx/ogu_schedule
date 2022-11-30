import typing
from datetime import datetime, timedelta

import pytz
from aiogram import Dispatcher
from aiogram.utils.executor import Executor
from tortoise.expressions import Q
from loguru import logger

from schedule_ogu.api import HTTPClient
from schedule_ogu import (ScheduleSubjectModel,
                          StatsModel,
                          ActionStats,
                          ScheduleTime,
                          FacultyModel,
                          DepartmentModel,
                          EmployeeModel,
                          GroupModel,
                          Years,
                          DayType,
                          UserModel,
                          UserType,
                          ExamModel
                          )


class ScheduleService:
    http: HTTPClient = HTTPClient()

    @classmethod
    async def init(cls):
        await cls.http.init()
        last_update = await StatsModel.filter(action=ActionStats.update_data).order_by("-datetime").first()
        if not last_update or last_update.datetime < (datetime.utcnow() - timedelta(days=365)).astimezone(pytz.utc):
            await cls.update_data()

    @classmethod
    async def fetch_schedule(cls,
                             user: UserModel,
                             *,
                             week_delta: int = 0
                             ):

        if user.type == UserType.Student:
            schedule = await cls.http.get_schedule_student(user.group_id,
                                                           ScheduleTime.compute_current_week() + week_delta)
            user_q = Q(group_id=user.group_id)
        else:
            schedule = await cls.http.get_schedule_employee(user.employee_id,
                                                            ScheduleTime.compute_current_week() + week_delta)
            user_q = Q(employee_id=user.employee_id)
        if not schedule:
            return
        await ScheduleSubjectModel.filter(user_q &
                                          Q(date__gte=ScheduleTime.compute_timestamp(week_delta=week_delta)) &
                                          Q(date__lte=ScheduleTime.compute_timestamp(week_delta=week_delta+1))).delete()

        for day in schedule.days.values():
            subjects = [ScheduleSubjectModel(**subject.dict(exclude={"employee_name",
                                                                     "employee_second_name",
                                                                     "employee_middle_name"}))
                        for subject in day.subjects]

            await ScheduleSubjectModel.bulk_create(subjects, ignore_conflicts=True)
        await StatsModel.create(action=ActionStats.update_schedule, extra=f"{user.id}", datetime=datetime.utcnow())
        logger.info("Updated schedule for user {user_id}", user_id=user.id)

    @classmethod
    async def fetch_exams(cls,
                          user: UserModel,
                          ) -> typing.Optional[typing.List[ExamModel]]:

        if user.type == UserType.Student:
            schedule = await cls.http.get_exams_student(user.group_id)
            user_q = Q(group_id=user.group_id)
        else:
            schedule = await cls.http.get_exams_employee(user.employee_id)
            user_q = Q(employee_id=user.employee_id)
        if not schedule:
            return
        await ExamModel.filter(user_q).delete()

        subjects = [ExamModel(**exam.dict(exclude={"employee_name",
                                                   "employee_second_name",
                                                   "employee_middle_name"}))
                    for exam in schedule]

        await ExamModel.bulk_create(subjects, ignore_conflicts=True)
        await StatsModel.create(action=ActionStats.update_exams, extra=f"{user.id}", datetime=datetime.utcnow())
        logger.info("Updated exams for user {user_id}", user_id=user.id)
        return await cls.get_exams(user)

    @classmethod
    async def get_exams(cls,
                        user: UserModel,
                        ) -> list[ExamModel]:
        if user.type == UserType.Student:
            user_q = Q(group_id=user.group_id)
        else:
            user_q = Q(employee_id=user.employee_id)
        data = await ExamModel.filter(user_q).prefetch_related("employee", "group")

        if data:
            last_update = (await StatsModel
                           .filter(action=ActionStats.update_exams, extra=f"{user.id}")
                           .order_by("-datetime")
                           .first()
                           )
            if last_update and last_update.datetime > (datetime.utcnow() - timedelta(hours=6)).astimezone(pytz.utc):
                logger.info("Skipped exams update for user {user_id} rate-limited", user_id=user.id)
                return data

        return await cls.fetch_exams(user)

    @classmethod
    async def get_schedule(cls,
                           user: UserModel,
                           *,
                           week_delta: int = 0,
                           ) -> typing.List[ScheduleSubjectModel]:
        if user.type == UserType.Student:
            user_q = Q(group_id=user.group_id)
        else:
            user_q = Q(employee_id=user.employee_id)
        data = (await ScheduleSubjectModel.filter(user_q &
                                                  Q(date__gte=ScheduleTime.compute_timestamp(week_delta=week_delta)) &
                                                  Q(date__lte=ScheduleTime.compute_timestamp(week_delta=week_delta+1)))
                .prefetch_related("employee", "group"))

        if data:
            last_update = (await StatsModel
                           .filter(action=ActionStats.update_schedule, extra=f"{user.id}")
                           .order_by("-datetime")
                           .first()
                           )
            if last_update and last_update.datetime > (datetime.utcnow() - timedelta(hours=6)).astimezone(pytz.utc):
                logger.info("Skipped schedule update for user {user_id} rate-limited", user_id=user.id)
                return data

        await cls.fetch_schedule(user, week_delta=week_delta)
        return await cls.get_schedule(user, week_delta=week_delta)

    @classmethod
    async def get_schedule_day(cls,
                               user: UserModel,
                               day: DayType,
                               *,
                               week_delta: int = 0,
                               past: bool = False,
                               ) -> typing.List[ScheduleSubjectModel]:
        if user.type == UserType.Student:
            user_q = Q(group_id=user.group_id)
        else:
            user_q = Q(employee_id=user.employee_id)

        data = (await ScheduleSubjectModel
                .filter(user_q &
                        Q(date=ScheduleTime.compute_timestamp(day=day, past=past)))
                .prefetch_related("employee", "group"))
        if data:
            last_update = (await StatsModel
                           .filter(action=ActionStats.update_schedule, extra=f"{user.id}")
                           .order_by("-datetime")
                           .first()
                           )
            if last_update and last_update.datetime > (datetime.utcnow() - timedelta(hours=3)).astimezone(pytz.utc):
                logger.info("Skipped schedule update for user {user_id} rate-limited", user_id=user.id)
                return data

        await cls.fetch_schedule(user, week_delta=week_delta)
        return await cls.get_schedule_day(user, day, week_delta=week_delta, past=past)

    @classmethod
    async def update_data(cls):
        faculties = await cls.update_faculties()
        for faculty in faculties:
            departments = await cls.update_departments(faculty.id)
            for department in departments:
                await cls.update_employees(department.id)
            await cls.update_groups(faculty.id)

        await StatsModel.create(action=ActionStats.update_data, datetime=datetime.utcnow())

    @classmethod
    async def update_faculties(cls) -> typing.List[FacultyModel]:
        faculties = await cls.http.get_faculties()
        await FacultyModel.all().delete()
        faculty_models = [FacultyModel(id=faculty.id,
                                       title=faculty.title,
                                       short_title=faculty.short_title) for faculty in faculties]
        await FacultyModel.bulk_create(faculty_models, ignore_conflicts=True)
        await StatsModel.create(action=ActionStats.update_faculties, datetime=datetime.utcnow())
        return faculty_models

    @classmethod
    async def update_departments(cls, faculty_id: int) -> typing.List[DepartmentModel]:
        await DepartmentModel.filter(Q(faculty_id=faculty_id)).delete()
        departments = await cls.http.get_departments(faculty_id)
        department_models = [DepartmentModel(id=department.id,
                                             title=department.title,
                                             short_title=department.short_title,
                                             faculty_id=faculty_id) for department in departments]
        await DepartmentModel.bulk_create(department_models, ignore_conflicts=True)
        await StatsModel.create(action=ActionStats.update_departments, datetime=datetime.utcnow())
        return department_models

    @classmethod
    async def update_employees(cls, department_id: int):
        await EmployeeModel.filter(Q(department_id=department_id)).delete()
        employees = await cls.http.get_employees(department_id)
        employee_models = [EmployeeModel(id=employee.id,
                                         name=employee.name,
                                         second_name=employee.second_name,
                                         middle_name=employee.middle_name,
                                         department_id=department_id) for employee in employees]
        await EmployeeModel.bulk_create(employee_models, ignore_conflicts=True)
        await StatsModel.create(action=ActionStats.update_employees, datetime=datetime.utcnow())
        return employee_models

    @classmethod
    async def update_groups(cls, faculty_id: int):
        await GroupModel.filter(Q(faculty_id=faculty_id)).delete()

        for course in Years:
            groups = await cls.http.get_groups(faculty_id, course)
            if not groups:
                continue
            group_models = [GroupModel(id=group.id,
                                       course=course,
                                       direction=group.direction,
                                       level=group.level.value,
                                       name=group.name,
                                       faculty_id=faculty_id) for group in groups]

            await GroupModel.bulk_create(group_models, ignore_conflicts=True)
            await StatsModel.create(action=ActionStats.update_groups, datetime=datetime.utcnow())

    @classmethod
    async def get_faculty_views(cls):
        data = await FacultyModel.all().prefetch_related("groups")
        return data

    @classmethod
    async def on_startup(cls, _: Dispatcher):
        await cls.init()

    @classmethod
    async def on_shutdown(cls, _: Dispatcher):
        await cls.http.close()

    @classmethod
    def setup(cls, executor: Executor):
        executor.on_startup(cls.on_startup)
        executor.on_shutdown(cls.on_shutdown)
