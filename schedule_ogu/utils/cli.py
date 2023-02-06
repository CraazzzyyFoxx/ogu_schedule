import asyncio
import functools

import click

from loguru import logger

try:
    import aiohttp_autoreload
except ImportError:
    aiohttp_autoreload = None


def start():
    from schedule_ogu import misc
    from schedule_ogu.utils import logging

    logging.setup()
    misc.setup()


@click.group()
def cli():
    from schedule_ogu.utils import logging

    logging.setup()


def auto_reload_mixin(func):
    @click.option(
        "--autoreload", is_flag=True, default=False, help="Reload application on file changes"
    )
    @functools.wraps(func)
    def wrapper(autoreload: bool, *args, **kwargs):
        if autoreload and aiohttp_autoreload:
            logger.warning(
                "Application started in live-reload mode. Please disable it in production!"
            )
            aiohttp_autoreload.start()
        elif autoreload and not aiohttp_autoreload:
            click.echo("`aiohttp_autoreload` is not installed.", err=True)
        return func(*args, **kwargs)

    return wrapper


@cli.command()
@click.option("--skip-updates", is_flag=True, default=False, help="Skip pending updates")
@auto_reload_mixin
def polling(skip_updates: bool):
    """
    Start application in polling mode
    """
    from schedule_ogu import misc
    asyncio.run(misc.setup())
