from pydantic import BaseSettings


class DatabaseConfig(BaseSettings):
    db: str

    class Config:
        env_file = ".env"
        env_prefix = "sqlite_"


db_config = DatabaseConfig()


tortoise_config = {
    "connections": {
        "default": {
            "engine": "tortoise.backends.sqlite",
            "credentials": {
                "file_path": "db.db"},
        }
    },
    "apps": {
        "main": {
            "models": ["ScheduleOGU.core.models"],
            "default_connection": "default",
        }
    },
}