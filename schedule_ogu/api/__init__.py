import asyncio
import time
import typing
import typing as t
from datetime import datetime, timedelta

import aiohttp
import pytz

from urllib.parse import quote
from aiohttp import ClientConnectorError
from fake_useragent import UserAgent
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from loguru import logger

from config import bot_config
from schedule_ogu.utils.time import ScheduleTime
from schedule_ogu.models.enums import Years
from schedule_ogu.models.db import UserAgentModel, CookieModel

from .models import (ScheduleEntryHTTP,
                     StudentGroupHTTP,
                     FacultyHTTP,
                     DepartmentHTTP,
                     EmployeeHTTP, ScheduleHTTP,
                     ExamHTTP)

from .utils import flatten_error_dict, json_or_text
from .erorrs import HTTPException


class Route:
    BASE: t.ClassVar[str] = 'https://oreluniver.ru'

    def __init__(self, method: str, path: str, **parameters: t.Any) -> None:
        self.path: str = path
        self.method: str = method
        url = self.BASE + self.path
        if parameters:
            url = url.format_map({k: quote(v) if isinstance(v, str) else v for k, v in parameters.items()})
        self.url: str = url


class HTTPClient:
    """Represents an HTTP client sending HTTP requests to the oreluniver.ru"""

    def __init__(
            self,
            loop: t.Optional[asyncio.AbstractEventLoop] = None
    ) -> None:
        self.loop: asyncio.AbstractEventLoop = asyncio.get_event_loop() if loop is None else loop

        self.__session: t.Optional[aiohttp.ClientSession] = None
        self.user_agent: t.Optional[str] = ""
        self.cookie: t.Optional[str] = ""

    async def init(self):
        logger.info("Starting API (oreluniver.ru)")
        # Necessary to get aiohttp to stop complaining about session creation
        self.__session = aiohttp.ClientSession(loop=self.loop)
        user_agent = await UserAgentModel.filter().order_by("-datetime").first()
        if user_agent:
            self.user_agent = user_agent.extra
        cookie = await CookieModel.filter().order_by("-datetime").first()
        if cookie:
            self.cookie = cookie.extra

        if not self.cookie or not self.user_agent:
            await self.update_cookies()

    async def close(self) -> None:
        if self.__session:
            await self.__session.close()

    async def update_cookies(self):
        user_agent = await UserAgentModel.filter().order_by("-datetime").first()
        if user_agent and user_agent.datetime > (datetime.utcnow() - timedelta(minutes=1)).astimezone(pytz.utc):
            raise RuntimeError('Unreachable code in HTTP handling')

        chrome_options = webdriver.ChromeOptions()
        ua = UserAgent()
        chrome_options.add_argument(f'user-agent={self.user_agent}')
        self.user_agent = ua.chrome
        chrome_options.add_argument("--start-maximized")  # open Browser in maximized mode
        chrome_options.add_argument("--no-sandbox")  # bypass OS security model
        chrome_options.add_argument("--disable-dev-shm-usage")  # overcome limited resource problems
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)

        s = Service(executable_path=bot_config.chrome_driver_dir)
        driver = webdriver.Chrome(service=s, options=chrome_options)
        try:
            logger.info("Fetching cookies for user-agent {}", user_agent)
            driver.get(Route.BASE)
            time.sleep(5)
            cookie_btn = driver.find_element(By.XPATH, '/html/body/div[6]/div/div/div/div')
            cookie_btn.click()
            cookies = driver.get_cookies()
            logger.info("Fetched cookies {}", cookies)
            self.cookie = "".join(f'{cookie.get("name")}={cookie.get("value")}; ' for cookie in cookies)

            await UserAgentModel.create(extra=self.user_agent, datetime=datetime.utcnow())
            await CookieModel.create(extra=self.cookie, datetime=datetime.utcnow())

        except Exception as ex:
            logger.error(ex)
        finally:
            driver.close()
            driver.quit()

    async def request(self, route: Route, **kwargs: t.Any) -> t.Any:
        url = route.url
        method = route.method

        response: t.Optional[aiohttp.ClientResponse] = None
        data: t.Optional[t.Union[t.Dict[str, t.Any], str]] = None

        for tries in range(5):
            try:
                headers: t.Dict[str, str] = {"user-agent": self.user_agent, "cookie": self.cookie}

                async with self.__session.request("get", url, headers=headers, **kwargs) as response:
                    logger.debug('{method} {url} with {data} has returned {status}',
                                 method=method,
                                 url=url,
                                 data=kwargs.get('data'),
                                 status=response.status
                                 )

                    # even errors have text involved in them so this is safe to call
                    data = await json_or_text(response)
                    if data is None:
                        await self.update_cookies()
                        continue

                    # the request was successful so just return the text/json
                    if 300 > response.status >= 200:
                        logger.debug('{method} {url} has received {data}',
                                     method=method,
                                     url=url,
                                     data=data
                                     )
                        return data

                    # we've received a 500, 502, or 504, unconditional retry
                    if response.status in {500, 502, 504}:
                        await asyncio.sleep(1 + tries * 2)
                        continue

            # This is handling exceptions from the request
            except OSError as e:
                # Connection reset by peer
                if tries < 4 and e.errno in (54, 10054):
                    await asyncio.sleep(1 + tries * 2)
                    continue
                raise
            except ClientConnectorError:
                return None

        if response is not None:
            # We've run out of retries, raise.
            if response.status >= 500:
                raise HTTPException(response, data)

            raise HTTPException(response, data)

        raise RuntimeError('Unreachable code in HTTP handling')

    async def get_schedule_student(self, group_id: int, week_delta: int = 0) -> t.Optional[ScheduleHTTP]:
        timestamp = ScheduleTime.compute_timestamp_for_api(week_delta)
        route = Route('GET', '/schedule//{group_id}///{timestamp}/printschedule',
                      group_id=group_id,
                      timestamp=timestamp)
        data: dict = await self.request(route)
        if not data:
            return
        schedule = ScheduleHTTP(ScheduleTime.compute_timestamp(week_delta=week_delta),
                                sorted([ScheduleEntryHTTP.parse_obj(raw) for index, raw in data.items()
                                        if index.isdigit()],
                                       key=lambda x: x.date))
        return schedule

    async def get_schedule_employee(self, employee_id: int, week_delta: int = 0) -> t.Optional[ScheduleHTTP]:
        timestamp = ScheduleTime.compute_timestamp_for_api(week_delta=week_delta)
        route = Route('GET', '/schedule/{employee_id}////{timestamp}/printschedule',
                      employee_id=employee_id,
                      timestamp=timestamp)
        data: dict = await self.request(route)
        if not data:
            return
        return ScheduleHTTP(ScheduleTime.compute_timestamp(week_delta=week_delta),
                            sorted([ScheduleEntryHTTP.parse_obj(raw) for index, raw in data.items()
                                    if index.isdigit()],
                                   key=lambda x: x.date))

    async def get_groups(self, faculty_id: int, course: Years) -> t.List[StudentGroupHTTP]:
        route = Route('GET', '/schedule/{faculty_id}/{course}/grouplist', faculty_id=faculty_id, course=course.value)
        data: dict = await self.request(route)
        return [StudentGroupHTTP.parse_obj(raw) for raw in data]

    async def get_faculties(self) -> t.List[FacultyHTTP]:
        route = Route('GET', '/schedule/divisionlistforstuds')
        data = await self.request(route)
        return [FacultyHTTP.parse_obj(raw) for raw in data]

    async def get_departments(self, faculty_id: int) -> t.List[DepartmentHTTP]:
        route = Route('GET', '/schedule/{faculty_id}/kaflist', faculty_id=faculty_id)
        data: dict = await self.request(route)
        return [DepartmentHTTP.parse_obj(raw) for raw in data]

    async def get_employees(self, department_id: int) -> t.List[EmployeeHTTP]:
        route = Route('GET', '/schedule/{department_id}/preplist',
                      department_id=department_id)
        data: dict = await self.request(route)
        return [EmployeeHTTP.parse_obj(raw) for raw in data]

    async def get_employee(self, employee_id: int) -> EmployeeHTTP:
        route = Route('GET', '/employee/{employee_id}', employee_id=employee_id)
        data: dict = await self.request(route)
        return EmployeeHTTP.parse_obj(data)

    async def get_exams_student(self, group_id: int) -> typing.List[ExamHTTP]:
        route = Route('GET', '/schedule/{group_id}////printexamschedule', group_id=group_id)
        data: dict = await self.request(route)
        return sorted([ExamHTTP.parse_obj(raw) for raw in data],
                      key=lambda x: x.time)

    async def get_exams_employee(self, employee_id: int) -> typing.List[ExamHTTP]:
        route = Route('GET', '/schedule//{employee_id}///printexamschedule', employee_id=employee_id)
        data: dict = await self.request(route)
        return sorted([ExamHTTP.parse_obj(raw) for raw in data],
                      key=lambda x: x.time)
