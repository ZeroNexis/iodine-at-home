# 第三方库
from pathlib import Path
from fastapi import APIRouter, Request, HTTPException, Response
from fastapi.responses import FileResponse, RedirectResponse

# 本地库
from random import choice
import core.utils as utils
from core.types import oclm, Cluster
from core.logger import logger
from core.filesdb import FilesDB

router = APIRouter()


@router.get("/files/{path}", summary="通过 PATH 下载普通文件", tags=["public"])
async def download_path_file(hash: str):
    async with FilesDB() as filesdb:
        filedata = await filesdb.find_one("PATH", hash)

    if filedata:
        if len(oclm) == 0:
            return RedirectResponse(filedata["URL"], 302)
        else:
            cluster = Cluster(choice(oclm.list))
            await cluster.initialize()
            sign = utils.get_sign(filedata["HASH"], cluster.secret)
            url = utils.get_url(
                cluster.host, cluster.port, f"/download/{filedata['HASH']}", sign
            )
            return RedirectResponse(url, 302)
    else:
        raise HTTPException(404, detail="未找到该文件")
