import typing as t

import aiohttp

from .utils import flatten_error_dict


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