import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.services.database.base import Base

if TYPE_CHECKING:
    from app.services.database.models.apps import Apps


class AppActions(Base):
    __tablename__ = "app_actions"

    id: Mapped[int] = mapped_column(primary_key=True)
    app_id: Mapped[int] = mapped_column(ForeignKey("apps.id"), nullable=False)
    date_time: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False)
    type: Mapped[int] = mapped_column(Integer, nullable=False)

    app: Mapped["Apps"] = relationship(back_populates="actions")
