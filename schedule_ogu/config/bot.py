from pydantic import BaseSettings


class BotConfig(BaseSettings):
    token: str
    has_display: bool
    chrome_driver_dir: str
    superuser_startup_notifier: bool

    class Config:
        env_file = ".env"
        env_prefix = "bot_"


bot_config = BotConfig()
