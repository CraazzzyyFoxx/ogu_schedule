import typing as t
import json

import aiohttp


__all__ = ('flatten_error_dict',
           "json_or_text")


def flatten_error_dict(d: t.Dict[str, t.Any], key: str = '') -> t.Dict[str, str]:
    items: t.List[t.Tuple[str, str]] = []
    for k, v in d.items():
        new_key = key + '.' + k if key else k

        if isinstance(v, dict):
            try:
                _errors: t.List[t.Dict[str, t.Any]] = v['_errors']
            except KeyError:
                items.extend(flatten_error_dict(v, new_key).items())
            else:
                items.append((new_key, ' '.join(x.get('message', '') for x in _errors)))
        else:
            items.append((new_key, v))

    return dict(items)


async def json_or_text(response: aiohttp.ClientResponse) -> t.Union[t.Dict[str, t.Any], str]:
    if response.headers['content-type'] == 'application/json':
        return await response.json()

