import os
from dataclasses import dataclass

from dotenv import load_dotenv


load_dotenv()


@dataclass
class AppSettings:
    DB_USER = os.getenv("DB_USER")
    DB_HOST = os.getenv("DB_HOST")
    DB_NAME = os.getenv("DB_NAME")
    DB_PASSWORD = os.getenv("DB_PASSWORD")

    @property
    def db_uri(self) -> str:
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:5432/{self.DB_NAME}"


settings = AppSettings()
