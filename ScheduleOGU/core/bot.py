import logging
import typing as t

from aiogram import Bot
from tortoise import Tortoise
from tortoise.expressions import Q

from .http import HTTPClient
from .models import EmployeeModel, ScheduleSubjectModel
from .enums import DayType

from ..config import bot_config, tortoise_config
from ..utils import ScheduleTime

_log = logging.getLogger()


class Client(Bot):
    def __init__(self):
        super().__init__(bot_config.token)
        self.http: HTTPClient = HTTPClient()

    async def fetch_schedule(self, group_id: int, week: int = None) -> t.Dict[DayType, t.List[ScheduleSubjectModel]]:
        schedule = await self.http.get_schedule(group_id, week)

        schedule_data = {}

        for day, subjects in schedule.items():
            await ScheduleSubjectModel.filter(date=subjects[0].date.timestamp()).delete()
            for subject in subjects:
                employee_ = (await EmployeeModel
                             .update_or_create(id=subject.employee_id,
                                               name=subject.employee_name,
                                               second_name=subject.employee_second_name,
                                               middle_name=subject.employee_middle_name))

                subject_ = await ScheduleSubjectModel.create(name=subject.name,
                                                             type=subject.type,
                                                             number=subject.number,
                                                             audience=subject.audience,
                                                             building=subject.building,
                                                             group_id=group_id,
                                                             date=subject.date.timestamp(),
                                                             day=day,
                                                             zoom_link=subject.zoom_link,
                                                             zoom_password=subject.zoom_password,
                                                             employee_id=subject.employee_id
                                                             )
                subject_.employee = employee_[0]

                if schedule_data.get(day):
                    schedule_data[day].append(subject_)
                else:
                    schedule_data[day] = [subject_]

        return schedule_data

    async def get_schedule(self, group_id: int, week: int = None) -> t.Dict[DayType, t.List[ScheduleSubjectModel]]:
        data = (await ScheduleSubjectModel
                .filter(Q(date__gte=ScheduleTime.compute_timestamp(ScheduleTime.compute_week())) &
                        Q(date__lte=ScheduleTime.compute_timestamp(ScheduleTime.compute_week() + 1)))
                .prefetch_related("employee"))
        if not data:
            return await self.fetch_schedule(group_id, week)

        schedule_data = {}

        for subject_ in data:
            if schedule_data.get(subject_.day):
                schedule_data[subject_.day].append(subject_)
            else:
                schedule_data[subject_.day] = [subject_]
        return schedule_data

    async def connect_db(self) -> None:
        _log.info("Connecting to Database...")
        await Tortoise.init(config=tortoise_config)
        await Tortoise.generate_schemas(safe=True)
        _log.info("Connected to Database.")
