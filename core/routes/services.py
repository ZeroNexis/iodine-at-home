# 第三方库
from pathlib import Path
from random import choices
from fastapi import APIRouter, Request, HTTPException, Response
from fastapi.responses import FileResponse, RedirectResponse

# 本地库
import core.utils as utils
from core.types import oclm, Cluster, filesdb
from core.logger import logger

router = APIRouter()


@router.get("/files/{path:path}", summary="通过 PATH 下载普通文件", tags=["public"])
async def download_path_file(path: str):
    filedata = filesdb.find(None, f"files/{path}")

    if filedata:
        if len(oclm) == 0:
            return FileResponse(Path(f"./{filedata['url']}"))
        else:
            cluster = Cluster(oclm.random())
            await cluster.initialize()
            sign = utils.get_sign(filedata['hash'], cluster.secret)
            url = utils.get_url(
                cluster.host, cluster.port, f"/download/{filedata['hash']}", sign
            )
            return RedirectResponse(url, 302)
    else:
        raise HTTPException(404, detail="未找到该文件")
