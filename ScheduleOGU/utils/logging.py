import logging


FMT = "[{levelname:^7}] {name}: {message}"
FORMATS = {logging.DEBUG: FMT,
           logging.INFO: f"\33[36m{FMT}\33[0m",
           logging.WARNING: f"\33[33m{FMT}\33[0m",
           logging.ERROR: f"\33[31m{FMT}\33[0m",
           logging.CRITICAL: f"\33[1m\33[31m{FMT}\33[0m"

           }


class CustomFormatter(logging.Formatter):
    def format(self, record) -> str:
        log_fmt = FORMATS[record.levelno]
        formatter = logging.Formatter(log_fmt, style="{")
        return formatter.format(record)