"""
Simplest example.
"""

from io import BytesIO
from os import path
from typing import Annotated
from requests import Response

from fastapi import BackgroundTasks, FastAPI, Depends
from nc_py_api.ex_app import (
    ApiScope,
    UiFileActionHandlerInfo,
    LogLvl,
    nc_app,
    set_handlers,
    run_app
)
from nc_py_api import NextcloudApp, FsNode
from inference_gfpgan import upscale_image


APP = FastAPI()


def gfpgan_background(input_file: FsNode, nc: NextcloudApp, upscale: int):
    try:
        if upscale == 1:
            subj = "Restoring finished!"
            suffix = ("restored",)
        else:
            subj = "Up-scaling finished!"
            suffix = ("upscaled",)
        output_file = "{0}_{2}{1}".format(*path.splitext(input_file.user_path) + suffix)
        buf = BytesIO()
        nc.files.download2stream(input_file, buf)
        buf = upscale_image(buf, upscale=upscale)
        nc.files.upload_stream(output_file, buf)
        if nc.scope_allowed(ApiScope.NOTIFICATIONS):
            nc.notifications.create(subj, f"{output_file} is ready.")
    except Exception as e:
        nc.log(LogLvl.ERROR, str(e))
        if nc.scope_allowed(ApiScope.NOTIFICATIONS):
            nc.notifications.create("Error occurred", "Error information was written to log file")
    return Response()


@APP.post("/gfpgan_upscale")
async def gfpgan_restore(
        file: UiFileActionHandlerInfo,
        nc: Annotated[NextcloudApp, Depends(nc_app)],
        background_tasks: BackgroundTasks,
):
    background_tasks.add_task(gfpgan_background, file.actionFile.to_fs_node(), nc, 2)
    return Response()


@APP.post("/gfpgan_restore")
async def gfpgan_restore(
        file: UiFileActionHandlerInfo,
        nc: Annotated[NextcloudApp, Depends(nc_app)],
        background_tasks: BackgroundTasks,
):
    background_tasks.add_task(gfpgan_background, file.actionFile.to_fs_node(), nc, 1)
    return Response()


def enabled_handler(enabled: bool, nc: NextcloudApp) -> str:
    print(f"enabled={enabled}")
    try:
        if enabled:
            nc.ui.files_dropdown_menu.register("upscale", "Upscale", "/gfpgan_upscale", mime="image")
            nc.ui.files_dropdown_menu.register("restore", "Restore", "/gfpgan_restore", mime="image")
        else:
            nc.ui.files_dropdown_menu.unregister("upscale")
            nc.ui.files_dropdown_menu.unregister("restore")
    except Exception as e:
        return str(e)
    return ""


@APP.on_event("startup")
def initialization():
    set_handlers(APP, enabled_handler)


if __name__ == "__main__":
    run_app("main:APP", log_level="trace")
