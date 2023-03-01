import datetime

from pydantic import BaseSettings


class BotConfig(BaseSettings):
    token: str
    has_display: bool
    chrome_driver_dir: str
    superuser_startup_notifier: bool

    class Config:
        env_file = ".env"
        env_prefix = "bot_"


class DatabaseConfig(BaseSettings):
    db: str
    host: str
    password: str
    port: int
    user: str

    class Config:
        env_file = ".env"
        env_prefix = "postgres_"


# Rate-limit config

UNABLE_RATE_LIMIT = True

UPDATE_FETCH_SCHEDULE = datetime.timedelta(hours=3)
UPDATE_FETCH_EXAMS = datetime.timedelta(hours=3)
UPDATE_FETCH_FACULTIES = datetime.timedelta(hours=24)
UPDATE_FETCH_DEPARTMENTS = datetime.timedelta(hours=24)
UPDATE_FETCH_EMPLOYEES = datetime.timedelta(hours=24)
UPDATE_FETCH_EMPLOYEE = datetime.timedelta(hours=3)
UPDATE_FETCH_DATA = datetime.timedelta(days=180)


# Constants for calculating time
START_SEMESTER = int(datetime.datetime(2022, 8, 29).timestamp())
BASE_WEEK_DELTA = 0


# Interface constants
UNABLE_EXAM_BUTTON = False


bot_config = BotConfig()
db_config = DatabaseConfig()
tortoise_config = {
    "connections": {
        "default": {
            "engine": "tortoise.backends.asyncpg",
            "credentials": {
                "database": db_config.db,
                "host": db_config.host,  # db for docker
                "password": db_config.password,
                "port": db_config.port,
                "user": db_config.user,
            },
        }
    },
    "apps": {
        "main": {
            "models": ["schedule_ogu.models.db"],
            "default_connection": "default",
        }
    },
}
