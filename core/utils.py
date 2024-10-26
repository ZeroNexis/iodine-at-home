# 第三方库
import jwt
import time
import httpx
import base64
import hashlib
from random import choice

# 本地库
import core.const as const
from core.config import config
from core.logger import logger
from core.types import Cluster


# JWT 加密
def encode_jwt(data, secret: str | None = config.get("jwt-secret")):
    result = jwt.encode(data, secret, algorithm="HS256")
    return result


# JWT 解密
def decode_jwt(data, secret: str | None = config.get("jwt-secret")):
    result = jwt.decode(data, secret, algorithms=["HS256"])
    return result


def hum_convert(value: int):
    units = ["B", "KiB", "MiB", "GiB", "TiB", "PiB"]
    size = value
    for unit in units:
        if (size / 1024) < 1:
            return "%.2f%s" % (size, unit)
        size = size / 1024
    return f"{value:.2f}"


def to_url_safe_base64_string(byte_data):
    return base64.urlsafe_b64encode(byte_data).rstrip(b"=").decode("utf-8")


# 将整数转换为base36字符串
def base36encode(number):
    if not isinstance(number, int):
        raise TypeError("number must be an integer")
    if number < 0:
        raise ValueError("number must be positive")
    alphabet = "0123456789abcdefghijklmnopqrstuvwxyz"
    base36 = ""
    while number:
        number, i = divmod(number, 36)
        base36 = alphabet[i] + base36
    return base36 or alphabet[0]


# 获取节点 sign
def get_sign(path, secret):
    try:
        sha1 = hashlib.sha1()
    except Exception as e:
        logger.error(e)
        return None
    timestamp = int((time.time() + 5 * 60) * 1000)
    e = base36encode(timestamp)
    sign_data = (secret + path + e).encode("utf-8")
    sha1.update(sign_data)
    sign_bytes = sha1.digest()
    sign = to_url_safe_base64_string(sign_bytes).replace("=", "")
    return f"?s={sign}&e={e}"


# 获取节点mesure的url
def get_url(host: str, port: str, path: str, sign: str):
    url = f"https://{host}:{port}{path}{sign}"
    return url


# 对节点进行测速
async def measure_cluster(size: int, cluster: Cluster):
    path = f"/measure/{str(size)}"
    sign = get_sign(path, cluster.secret)
    url = get_url(cluster.host, cluster.port, path, sign)
    try:
        start_time = time.time()
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers={"User-Agent": const.user_agent}, timeout=10)
        end_time = time.time()
        elapsed_time = end_time - start_time
        # 计算测速时间
        bandwidth = size / elapsed_time * 8  # 计算带宽
        return [True, bandwidth]
    except Exception as e:
        return [False, e]
