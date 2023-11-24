from datetime import datetime

import asyncpg
from fastapi.encoders import jsonable_encoder
from sqlalchemy import insert, select
from sqlalchemy.orm import selectinload

from app.config import settings
from app.services.database.base import Base, async_session, engine
from app.services.database.models.apps import Apps
from app.services.database.models.apps_journal import AppActions


async def create_database():
    sys_conn = await asyncpg.connect(
        database='template1',
        user=settings.DB_USER,
        password=settings.DB_PASS
    )
    await sys_conn.execute(
        f'CREATE DATABASE "{settings.DB_NAME}" OWNER "{settings.DB_USER}"'
    )
    await sys_conn.close()


class AppsDAO:

    @classmethod
    async def check_db(cls):
        try:
            async with async_session() as session:
                await session.execute(select(Apps))
        except asyncpg.InvalidCatalogNameError:
            await create_database()
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)

    @classmethod
    async def insert_new_app(cls, path: str) -> int:
        async with async_session() as session:
            query = select(Apps).where(Apps.path == path)
            result = await session.execute(query)
            result = result.scalar_one_or_none()
            if not result:
                query = insert(Apps).values(
                    path=path
                ).returning(Apps)
                result = await session.execute(query)
                await session.commit()
                result = result.scalar_one_or_none()

            return result.id

    @classmethod
    async def insert_action(cls, db_id, action: int):
        async with async_session() as session:
            query = (insert(AppActions)
                     .values(app_id=db_id,
                             date_time=datetime.utcnow(),
                             type=action
                             ))
            await session.execute(query)
            await session.commit()

    @classmethod
    async def get_app_actions(cls):
        async with async_session() as session:
            query = (select(Apps)
            .options(
                selectinload(Apps.actions)
            ))

            result = await session.execute(query)
            return jsonable_encoder(result.scalars().all())
