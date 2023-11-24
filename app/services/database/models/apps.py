from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.services.database.base import Base

if TYPE_CHECKING:
    from app.services.database.models.apps_journal import AppActions


class Apps(Base):
    __tablename__ = "apps"

    id: Mapped[int] = mapped_column(primary_key=True)
    path: Mapped[str] = mapped_column(String)

    actions: Mapped[list["AppActions"]] = relationship(back_populates="app")
