import asyncio
import logging
import typing as t

import aiohttp

from urllib.parse import quote

from ...utils import ScheduleTime

from .models import ScheduleEntryHTTP, StudentGroupHTTP, FacultyHTTP, ScheduleHTTP
from .utils import flatten_error_dict, json_or_text
from .erorrs import HTTPException


_log = logging.getLogger(__name__)


class Route:
    BASE: t.ClassVar[str] = 'http://oreluniver.ru'

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
        self.__session: aiohttp.ClientSession = None  # type: ignore
        self.user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) " \
                               "Chrome/96.0.4664.174 YaBrowser/22.1.5.810 Yowser/2.5 Safari/537.36"

    async def init(self):
        # Necessary to get aiohttp to stop complaining about session creation
        self.__session = aiohttp.ClientSession(loop=self.loop)
        _log.info('Session Started')

    async def close(self) -> None:
        if self.__session:
            await self.__session.close()

    async def request(
            self,
            route: Route,
            **kwargs: t.Any,
    ) -> t.Any:
        url = route.url
        method = route.method

        # header creation
        headers: t.Dict[str, str] = {
            "Accept": "*/*",
            'User-Agent': self.user_agent,
        }

        kwargs['headers'] = headers

        response: t.Optional[aiohttp.ClientResponse] = None
        data: t.Optional[t.Union[t.Dict[str, t.Any], str]] = None

        for tries in range(5):
            try:
                async with self.__session.request("get", url, **kwargs) as response:
                    _log.debug('%s %s with %s has returned %s', method, url, kwargs.get('data'), response.status)

                    # even errors have text involved in them so this is safe to call
                    data = await json_or_text(response)

                    # the request was successful so just return the text/json
                    if 300 > response.status >= 200:
                        _log.debug('%s %s has received %s', method, url, data)
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

        if response is not None:
            # We've run out of retries, raise.
            if response.status >= 500:
                raise HTTPException(response, data)

            raise HTTPException(response, data)

        raise RuntimeError('Unreachable code in HTTP handling')

    async def get_schedule(self, group_id: int, week: int = None) -> ScheduleHTTP:
        timestamp = ScheduleTime.compute_timestamp_for_site(week)
        route = Route('GET', '/schedule//{group_id}///{timestamp}/printschedule', group_id=group_id,
                      timestamp=timestamp)
        data: dict = await self.request(route)
        data.pop("Authorization")

        return ScheduleHTTP(sorted([ScheduleEntryHTTP.parse_obj(raw) for raw in data.values()],
                                   key=lambda x: (x.date, x.number)))

    async def get_employee(self, employee_id: int):
        route = Route('GET', '/employee/{employee_id}', employee_id=employee_id)
        data = await self.request(route)
        return data

    async def get_groups(self, faculty_id: int, course: int) -> t.List[StudentGroupHTTP]:
        route = Route('GET', '/schedule/{faculty_id}/{course}/grouplist',
                      faculty_id=faculty_id,
                      course=course)
        data = await self.request(route)
        return [StudentGroupHTTP.parse_obj(raw) for raw in data]

    async def get_faculties(self) -> t.List[FacultyHTTP]:
        route = Route('GET', '/schedule/divisionlistforstuds')
        data = await self.request(route)
        return [FacultyHTTP.parse_obj(raw) for raw in data]
