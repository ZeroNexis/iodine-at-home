# 第三方库
import hmac
import time
import hashlib
from fastapi import APIRouter, Request, HTTPException, Response
from fastapi.responses import JSONResponse, PlainTextResponse

# 本地库
import core.utils as utils
import core.const as const
from core.types import Cluster


router = APIRouter()


@router.get(
    "/challenge", summary="颁发 challenge 码", tags=["nodes"]
)  # 颁发 challenge 验证码
async def get_challenge(response: Response, clusterId: str | None = ""):
    cluster = Cluster(clusterId)
    if await cluster.initialize():
        return {
            "challenge": utils.encode_jwt(
                {
                    "cluster_id": clusterId,
                    "iss": const.jwt_iss,
                    "exp": int(time.time()) + 1000 * 60 * 5,
                }
            )
        }
    else:
        raise HTTPException(status_code=404, detail="节点未找到")


@router.post("/token", summary="颁发令牌", tags=["nodes"])  # 颁发令牌
async def post_token(request: Request):
    content_type = request.headers.get("content-type", "")
    if "application/json" in content_type:
        data = await request.json()
    elif "application/x-www-form-urlencoded" in content_type:
        data = await request.form()
        data = dict(data)
    elif "multipart/form-data" in content_type:
        data = await request.form()
        data = dict(data)
    else:
        raise HTTPException(status_code=400, detail="不支持的媒体类型")

    clusterId = data.get("clusterId")
    challenge = data.get("challenge")
    signature = data.get("signature")

    cluster = Cluster(clusterId)
    if await cluster.initialize() == False:
        raise HTTPException(status_code=404, detail="节点未找到")
    h = hmac.new(cluster.secret.encode("utf-8"), digestmod=hashlib.sha256)
    if challenge is not None and isinstance(challenge, str):
        h.update(challenge.encode())
    else:
        raise HTTPException(status_code=401, detail="验证错误")
    if utils.decode_jwt(challenge)["cluster_id"] == clusterId and utils.decode_jwt(
        challenge
    )["exp"] > int(time.time()):
        if str(h.hexdigest()) == signature:
            ttl = 60 * 60 * 24 * 1000
            return JSONResponse(
                {
                    "token": utils.encode_jwt(
                        {
                            "cluster_id": clusterId,
                            "cluster_secret": cluster.secret,
                            "iss": const.jwt_iss,
                            "exp": int(time.time()) + ttl,
                        }
                    ),
                    "ttl": ttl,
                }
            )
        else:
            raise HTTPException(status_code=401, detail="错误的签名")
    else:
        raise HTTPException(status_code=401, detail="验证错误")
