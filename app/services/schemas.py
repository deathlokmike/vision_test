import datetime

from pydantic import BaseModel


class SAppStatus(BaseModel):
    path: str
    is_running: bool


class SAction(BaseModel):
    type: int
    date_time: datetime.datetime


class SAppJournal(BaseModel):
    path: str
    actions: list[SAction]