from fastapi.routing import APIRouter
from pydantic import TypeAdapter

from app.services.app_manager import app_manager
from app.services.database.dao import AppsDAO
from app.services.schemas import SAppJournal, SAppStatus

router = APIRouter(prefix="")


@router.get("/start")
async def run(app_path: str):
    return await app_manager.run_app(app_path)


@router.get("/kill")
async def kill(app_path: str):
    return await app_manager.kill_app(app_path)

@router.get("/kill_all")
async def kill():
    return await app_manager.kill_all()


@router.get("/app_list")
async def get_apps() -> list[SAppStatus]:
    await app_manager.fill_runnable_apps()
    return app_manager.available_apps


@router.get("/app_journal")
async def get_journal() -> list[SAppJournal]:
    result = await AppsDAO.get_app_actions()
    return TypeAdapter(list[SAppJournal]).validate_python(result)
