import logging
import typing as t
from pprint import pprint

from aiogram import Bot
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from tortoise import Tortoise
from tortoise.expressions import Q
from tortoise.query_utils import Prefetch

from .http import HTTPClient
from .models import EmployeeModel, ScheduleSubjectModel, FacultyModel, GroupModel, UserModel, ScheduleDayModel
from .enums import Years

from ..config import bot_config, tortoise_config
from ..utils import ScheduleTime

_log = logging.getLogger()


class Client(Bot):
    def __init__(self):
        super().__init__(bot_config.token)
        self.http: HTTPClient = HTTPClient()
        self.storage = MemoryStorage()

    async def on_startup(self, dispatcher):
        _log.info("Starting...")
        await self.http.init()
        await self.connect_db()
        # await self.fetch_groups()
        _log.info("Started.")

    async def on_shutdown(self, dispatcher):
        _log.info("Closing...")
        await self.http.close()
        await Tortoise.close_connections()
        await self.storage.close()
        await self.close()
        _log.info("Closed.")

    async def connect_db(self) -> None:
        _log.info("Connecting to Database...")
        await Tortoise.init(config=tortoise_config)
        await Tortoise.generate_schemas(safe=True)
        _log.info("Connected to Database.")

    async def get_schedule_for_user(self, message):
        user = await UserModel.filter(id=message.from_user.id).first()

        if user is None:
            await message.reply("Используйте команду /start.")
        return await self.get_schedule(user.group_id)

    async def fetch_schedule(self, group_id: int, week: int = None) -> t.List[ScheduleDayModel]:
        schedule = await self.http.get_schedule(group_id, week)

        for day in schedule.days.values():
            await ScheduleDayModel.filter(date=day.date).delete()
            day_ = await ScheduleDayModel.create(date=day.date,
                                                 day=day.day,
                                                 group_id=group_id)

            subjects_ = []
            for subject in day.subjects:
                (await EmployeeModel
                 .update_or_create(defaults={"id": subject.employee_id,
                                             "name": subject.employee_name,
                                             "second_name": subject.employee_second_name,
                                             "middle_name": subject.employee_middle_name},
                                   id=subject.employee_id))

                subjects_.append(ScheduleSubjectModel(name=subject.name,
                                                      type=subject.type,
                                                      number=subject.number,
                                                      audience=subject.audience,
                                                      building=subject.building,
                                                      zoom_link=subject.zoom_link,
                                                      zoom_password=subject.zoom_password,
                                                      employee_id=subject.employee_id,
                                                      day_id=day_.id
                                                      ))

            await ScheduleSubjectModel.bulk_create(subjects_)

        return await self.get_schedule(group_id, week)

    async def get_schedule(self, group_id: int, week: int = None) -> t.List[ScheduleDayModel]:
        data = (await ScheduleDayModel
                .filter(Q(group_id=group_id) &
                        Q(date__gte=ScheduleTime.compute_timestamp(ScheduleTime.compute_week())) &
                        Q(date__lte=ScheduleTime.compute_timestamp(ScheduleTime.compute_week() + 1)))
                .prefetch_related(Prefetch("subjects",
                                           queryset=ScheduleSubjectModel.all().prefetch_related("employee"))))

        if not data:
            return await self.fetch_schedule(group_id, week)
        return data

    async def fetch_groups(self):
        faculties = await self.http.get_faculties()
        groups_data = dict()

        await FacultyModel.all().delete()
        await GroupModel.all().delete()

        for faculty in faculties:
            faculty_ = await FacultyModel.create(**{"id": faculty.id,
                                                    "title": faculty.title,
                                                    "short_title": faculty.short_title})
            groups_data[faculty] = []

            for course in Years._member_map_.values():
                groups = await self.http.get_groups(faculty.id, course.value)
                if len(groups) == 0:
                    continue
                for group in groups:
                    await GroupModel.create(**{"id": group.id,
                                               "course": course,
                                               "direction": group.direction,
                                               "level": group.level.value,
                                               "name": group.name,
                                               "faculty_id": faculty_.id})
                    groups_data[faculty].append(group)

        return groups_data

    async def get_faculty_views(self):
        data = await FacultyModel.all().prefetch_related("groups")
        return data
