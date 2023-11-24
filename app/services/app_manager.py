import asyncio
import os
import signal
import subprocess

import psutil

from app.services.connection_manager import manager
from app.services.database.dao import AppsDAO
from app.services.schemas import SAppStatus


def _get_target_path(path: str) -> str:
    target_path = subprocess.check_output(
        [
            "powershell",
            '(New-Object -ComObject WScript.Shell).CreateShortcut("{}").TargetPath'.format(
                path
            ),
        ],
        text=True,
    ).strip()
    return target_path

def _get_parent_pid(path: str):
    path = path[path.rfind('/') + 1:]
    for proc in psutil.process_iter(attrs=["pid", "ppid", "name"]):
        try:
            if proc.name() == path:
                ppid = proc.ppid()
                if psutil.pid_exists(ppid):
                    app_process = psutil.Process(ppid)
                    if app_process.name() != path:
                        return proc.pid
                else:
                    return proc.pid
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

    return -1

class AppManager:
    def __init__(self):
        self._user_path = os.path.expanduser("~") + "\\Desktop"
        self._available_apps = dict()
        self._checked_lnk: set[str] = set()

    @property
    def available_apps(self) -> list[SAppStatus]:
        result: list[SAppStatus] = []
        for app_path, app_info in self._available_apps.items():
            app_status = SAppStatus(path=app_path,
                                    is_running=False if app_info["pid"] == -1 else True)
            result.append(app_status)
        return result

    def _get_app_paths(self) -> set[str]:
        temp_lnk = set()
        for file in os.listdir(self._user_path):
            if file.endswith(".lnk"):
                full_path = f"{self._user_path}\\{file}"
                if full_path not in self._checked_lnk:
                    self._checked_lnk.add(full_path)
                    temp_lnk.add(full_path)
        return temp_lnk

    async def _track_app_state(self):
        while True:
            for app_path, app_info in self._available_apps.items():
                app_pid = app_info["pid"]
                if app_pid == -1:
                    continue
                elif psutil.pid_exists(app_pid):
                    app_process = psutil.Process(app_pid)
                    if app_process.name() != app_path.split("/")[-1]:
                        app_info["pid"] = -1
                else:
                    app_info["pid"] = -1
                    await manager.broadcast(app_path)
                    await AppsDAO.insert_action(self._available_apps[app_path]["db_id"], 0)
            await asyncio.sleep(0.5)

    async def _add_to_available_apps(self, path: str):
        path = path.replace("\\", "/")
        if path not in self._available_apps.keys():
            db_id = await AppsDAO.insert_new_app(path)
            self._available_apps[path] = {"pid": _get_parent_pid(path), "db_id": db_id}

    async def fill_runnable_apps(self):
        await AppsDAO.check_db()
        for path in self._get_app_paths():
            target_path = _get_target_path(path)
            if target_path.endswith(".exe"):
                await self._add_to_available_apps(target_path)
        asyncio.create_task(self._track_app_state())

    async def run_app(self, app_path: str):
        try:
            if self._available_apps[app_path]["pid"] == -1:
                subprocess.Popen(app_path)
                self._available_apps[app_path]["pid"] = _get_parent_pid(app_path)
                await AppsDAO.insert_action(self._available_apps[app_path]["db_id"], 1)
                return "Приложение успешно включено"
            return "Приложение уже включено"
        except KeyError:
            return "Приложение не существует"
        
    async def _terminate_app(self, app_path: str):
        if psutil.pid_exists(self._available_apps[app_path]["pid"]):
            os.kill(self._available_apps[app_path]["pid"], signal.SIGTERM)
        self._available_apps[app_path]["pid"] = -1
        await AppsDAO.insert_action(self._available_apps[app_path]["db_id"], 0)
        
    async def kill_app(self, app_path: str):
        try:
            if self._available_apps[app_path]["pid"] != -1:
                await self._terminate_app(app_path)
                return "Приложение успешно выключено"
            return "Приложение не включено"
        except KeyError:
            return "Приложение не существует"
        
    async def kill_all(self):
        for app_path, app_info in self._available_apps.items():
            if app_info["pid"] != -1:
                await self._terminate_app(app_path)
        return "Все приложения выключены"


app_manager = AppManager()
