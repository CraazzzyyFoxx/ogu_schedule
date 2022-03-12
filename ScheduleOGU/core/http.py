import asyncio
import logging
import typing as t

import aiohttp

from urllib.parse import quote

from ScheduleOGU import (ScheduleEntryHTTP,
                         DayType,
                         try_value,
                         flatten_error_dict,
                         json_or_text,
                         ScheduleTime)

_log = logging.getLogger(__name__)


class HTTPException(Exception):
    def __init__(self, response: aiohttp.ClientResponse, message: t.Optional[t.Union[str, t.Dict[str, t.Any]]]):
        self.response: aiohttp.ClientResponse = response
        self.status: int = response.status
        self.code: int
        self.text: str
        if isinstance(message, dict):
            self.code = message.get('code', 0)
            base = message.get('message', '')
            errors = message.get('errors')
            if errors:
                errors = flatten_error_dict(errors)
                helpful = '\n'.join('In %s: %s' % e for e in errors.items())
                self.text = base + '\n' + helpful
            else:
                self.text = base
        else:
            self.text = message or ''
            self.code = 0

        fmt = '{0.status} {0.reason} (error code: {1})'
        if len(self.text):
            fmt += ': {2}'

        super().__init__(fmt.format(self.response, self.code, self.text))


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

    async def static_login(self):
        # Necessary to get aiohttp to stop complaining about session creation
        self.__session = aiohttp.ClientSession(loop=self.loop)
        _log.info('Session Started')

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

    async def get_schedule(self, group_id: int, week: int = None) -> t.Dict[DayType, t.List[ScheduleEntryHTTP]]:
        timestamp = ScheduleTime.compute_timestamp_for_site(week)
        route = Route('GET', '/schedule//{group_id}///{timestamp}/printschedule', group_id=group_id,
                      timestamp=timestamp)
        data: dict = await self.request(route)
        data.pop("Authorization")
        schedule = dict()

        for subject in [ScheduleEntryHTTP.parse_obj(raw) for raw in data.values()]:
            if subject.day_week not in schedule.keys():
                schedule[try_value(DayType, subject.day_week)] = [subject]
            else:
                schedule[try_value(DayType, subject.day_week)].append(subject)
        return schedule

    async def get_employee(self, employee_id: int):
        route = Route('GET', '/employee/{employee_id}', employee_id=employee_id)
        data = await self.request(route)
        return data
