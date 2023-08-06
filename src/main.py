"""
Simplest example.
"""

from io import BytesIO
from os import environ, path
from typing import Annotated
from requests import Response

import uvicorn
from fastapi import BackgroundTasks, FastAPI, Depends
from nc_py_api import (
    ApiScope,
    GuiActionFileInfo,
    GuiFileActionHandlerInfo,
    LogLvl,
    NextcloudApp,
    enable_heartbeat,
    nc_app,
    set_enabled_handler,
    set_scopes,
)
from inference_gfpgan import upscale_image


APP = FastAPI()


def gfpgan_background(input_params: GuiActionFileInfo, nc: NextcloudApp, upscale: int):
    try:
        full_path = path.join(input_params.directory, input_params.name)
        if upscale == 1:
            subj = "Restoring finished!"
            suffix = ("restored",)
        else:
            subj = "Up-scaling finished!"
            suffix = ("upscaled",)
        output_file = "{0}_{2}{1}".format(*path.splitext(full_path) + suffix)
        buf = BytesIO()
        nc.files.download2stream(full_path, buf)
        buf = upscale_image(buf, upscale=upscale)
        nc.files.upload_stream(output_file, buf)
        nc.users.notifications.create(subj, f"{output_file} is ready.")
    except Exception as e:
        nc.log(LogLvl.ERROR, str(e))
        nc.users.notifications.create("Error occurred", "Error information was written to log file")
    return Response()


@APP.post("/gfpgan_upscale")
async def gfpgan_restore(
        file: GuiFileActionHandlerInfo,
        nc: Annotated[NextcloudApp, Depends(nc_app)],
        background_tasks: BackgroundTasks,
):
    background_tasks.add_task(gfpgan_background, file.actionFile, nc, 2)
    return Response()


@APP.post("/gfpgan_restore")
async def gfpgan_restore(
        file: GuiFileActionHandlerInfo,
        nc: Annotated[NextcloudApp, Depends(nc_app)],
        background_tasks: BackgroundTasks,
):
    background_tasks.add_task(gfpgan_background, file.actionFile, nc, 1)
    return Response()


def enabled_handler(enabled: bool, nc: NextcloudApp) -> str:
    print(f"enabled={enabled}")
    try:
        if enabled:
            nc.gui.files_dropdown_menu.register("upscale", "Upscale", "/gfpgan_upscale", mime="image")
            nc.gui.files_dropdown_menu.register("restore", "Restore", "/gfpgan_restore", mime="image")
        else:
            nc.gui.files_dropdown_menu.unregister("upscale")
            nc.gui.files_dropdown_menu.unregister("restore")
    except Exception as e:
        return str(e)
    return ""


@APP.on_event("startup")
def initialization():
    set_enabled_handler(APP, enabled_handler)
    # In this minimal case, we don't need any scopes at all, because we only use `log`, which is a `BASIC` scope.
    set_scopes(APP, {"required": [ApiScope.DAV], "optional": [ApiScope.NOTIFICATIONS]})
    enable_heartbeat(APP)


# Next lines can be replaced with: `nc_py_api.start_app()` call. Here we just show that example uses `uvicorn`
if __name__ == "__main__":
    uvicorn.run("main:APP", host=environ.get("APP_HOST", "127.0.0.1"), port=int(environ["APP_PORT"]), log_level="trace")
