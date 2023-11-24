from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.services.app_manager import app_manager

router = APIRouter(tags=["Шаблоны"])

templates = Jinja2Templates(directory="app/templates")


async def get_available():
    await app_manager.fill_runnable_apps()
    return app_manager.available_apps


@router.get("/index", response_class=HTMLResponse)
async def get_user_appointments_page(
        request: Request, info=Depends(get_available)
):
    return templates.TemplateResponse(
        name="index.html",
        context={
            "request": request,
            "apps": info,
        },
    )
