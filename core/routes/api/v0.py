# 第三方库
from fastapi import APIRouter, Request, HTTPException, Response
from fastapi.responses import FileResponse, HTMLResponse, PlainTextResponse

# 本地库
from core.types import oclm
from core.mdb import cdb


router = APIRouter()


@router.get("/version")
async def get_version_data():
    return {
        "name": "iodine-at-home",
        "version": "1.12.1",
        "description": "开源的文件分发主控，并尝试兼容 OpenBMCLAPI 客户端",
        "repository": {
            "type": "git",
            "url": "git+https://github.com/ZeroNexis/iodine-at-home",
        },
        "author": "Dongyanmio <dongyanmio@outlook.com>",
        "license": "MIT",
        "bugs": {"url": "https://github.com/ZeroNexis/iodine-at-home/issues"},
        "homepage": "https://github.com/ZeroNexis/iodine-at-home#readme",
    }


@router.get("/dashboard")
async def get_dashboard_data():
    return {
        "currentNodes": len(oclm),
    }


@router.get("/rank")
async def get_rank_data():
    result = []
    all_data = await cdb.get_all()
    for data in all_data:
        data["_id"] = str(data["_id"])
        if oclm.include(data["_id"]):
            data["isEnabled"] = True
        else:
            data["isEnabled"] = False
        rdata = {
            k: v for k, v in data.items() if k in ["_id", "name", "isEnabled", "isBanned"]
        }
        result.append(rdata)
    return result