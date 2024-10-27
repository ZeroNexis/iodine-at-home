# 第三方库
import io
import heapq
from random import choices
from typing import Optional

# 本地库
from core.mdb import cdb


class Cluster:
    def __init__(self, cluster_id: str):
        self.id = cluster_id

    async def initialize(self):
        data = await cdb.find_cluster(self.id)
        if data[0]:
            # 正常数据
            self.name = str(data[1]["name"])
            self.secret = str(data[1]["secret"])
            self.bandwidth = int(data[1]["bandwidth"])
            self.measureBandwidth = int(data[1].get("measureBandwidth", 0))
            self.trust = int(data[1].get("trust", 0))
            self.isBanned = bool(data[1].get("isBanned", False))
            self.ban_reason = str(data[1].get("ban_reason", ""))
            self.host = str(data[1].get("host", ""))
            self.port = int(data[1].get("port", 0))
            self.version = str(data[1].get("version", ""))
            self.runtime = str(data[1].get("runtime", ""))
            self.cert_fullchain = str(data[1].get("cert_fullchain", ""))
            self.cert_privkey = str(data[1].get("cert_privkey", ""))
            self.cert_expiry = str(data[1].get("cert_expiry", ""))
            self.weight = self.trust + self.bandwidth + self.measureBandwidth
            return True
        else:
            return False

    async def edit(
        self,
        name: str = None,
        secret: str = None,
        bandwidth: int = None,
        measureBandwidth: int = None,
        trust: int = None,
        isBanned: bool = None,
        ban_reason: str = None,
        host: str = None,
        port: int = None,
        version: str = None,
        runtime: str = None,
        cert_fullchain: str = None,
        cert_privkey: str = None,
        cert_expiry: str = None,
    ):
        result = await cdb.edit_cluster(
            self.id,
            name,
            secret,
            bandwidth,
            measureBandwidth,
            trust,
            isBanned,
            ban_reason,
            host,
            port,
            version,
            runtime,
            cert_fullchain,
            cert_privkey,
            cert_expiry,
        )
        if result:
            await self.initialize()
        return result

    def json(self):
        return {
            "id": self.id,
            "name": self.name,
            "secret": self.secret,
            "bandwidth": self.bandwidth,
            "measureBandwidth": self.measureBandwidth,
            "trust": self.trust,
            "isBanned": self.isBanned,
            "ban_reason": self.ban_reason,
            "host": self.host,
            "port": self.port,
            "version": self.version,
            "runtime": self.runtime,
        }


class OCLManager:
    def __init__(self):
        self.id_list = []
        self.weight_list = []

    def __len__(self):
        return len(self.id_list)

    def append(self, cluster_id: str, weight: float):
        if cluster_id not in self.id_list:
            self.id_list.append(cluster_id)
            self.weight_list.append(weight)

    def remove(self, cluster_id: str):
        if cluster_id in self.id_list:
            self.weight_list.remove(self.weight_list[self.id_list.index(cluster_id)])
            self.id_list.remove(cluster_id)

    def update(self, cluster_id: str, weight: float):
        if cluster_id in self.id_list:
            self.weight_list[self.id_list.index(cluster_id)] = weight

    def include(self, cluster_id: str):
        return cluster_id in self.id_list

    def random(self) -> str:
        return choices(self.id_list, self.weight_list)[0]


oclm = OCLManager()


class FilesDB:
    def __init__(self):
        self.hash_list = []
        self.size_list = []
        self.mtime_list = []
        self.url_list = []

    def append(self, hash: str, size: int, mtime: int, url: str):
        if hash not in self.hash_list:
            self.hash_list.append(hash)
            self.size_list.append(size)
            self.mtime_list.append(mtime)
            self.url_list.append(url)

    def remove(self, hash: str):
        if hash in self.hash_list:
            self.size_list.remove(self.size_list[self.hash_list.index(hash)])
            self.mtime_list.remove(self.mtime_list[self.hash_list.index(hash)])
            self.url_list.remove(self.url_list[self.hash_list.index(hash)])
            self.hash_list.remove(hash)

    def find(self, hash: str | None = None, url: str | None = None):
        if hash is not None:
            if hash in self.hash_list:
                return {
                    "hash": hash,
                    "size": self.size_list[self.hash_list.index(hash)],
                    "mtime": self.mtime_list[self.hash_list.index(hash)],
                    "url": self.url_list[self.hash_list.index(hash)],
                }
            else:
                return None
        elif url is not None:
            if url in self.url_list:
                return {
                    "hash": self.hash_list[self.url_list.index(url)],
                    "size": self.size_list[self.url_list.index(url)],
                    "mtime": self.mtime_list[self.url_list.index(url)],
                    "url": url,
                }
            else:
                return None
        else:
            return None


filesdb = FilesDB()


# 本段修改自 TTB-Network/python-openbmclapi 中部分代码
# 仓库链接: https://github.com/TTB-Network/python-openbmclapi
# 源代码使用 MIT License 协议开源 | Copyright (c) 2024 TTB-Network
class Avro:
    def __init__(self, initial_bytes: bytes = b"", encoding: str = "utf-8") -> None:
        self.io = io.BytesIO(initial_bytes)
        self.encoding = encoding

    def read(self, __size: int = None):
        return self.io.read(__size)

    def readIntegetr(self):
        value = self.read(4)
        return (value[0] << 24) + (value[1] << 16) + (value[2] << 8) + (value[3] << 0)

    def readBoolean(self):
        return bool(int.from_bytes(self.read(1), byteorder="big"))

    def readShort(self):
        value = self.read(2)
        if value[0] | value[1] < 0:
            raise EOFError()
        return (value[0] << 8) + (value[1] << 0)

    def readLong(self) -> int:
        value = list(self.read(8))
        value = (
            (value[0] << 56)
            + ((value[1] & 255) << 48)
            + ((value[2] & 255) << 40)
            + ((value[3] & 255) << 32)
            + ((value[4] & 255) << 24)
            + ((value[5] & 255) << 16)
            + ((value[6] & 255) << 8)
            + ((value[7] & 255) << 0)
        )
        return value - 2**64 if value > 2**63 - 1 else value

    def readVarInt(self) -> int:
        b = ord(self.read(1))
        n = b & 0x7F
        shift = 7
        while (b & 0x80) != 0:
            b = ord(self.read(1))
            n |= (b & 0x7F) << shift
            shift += 7
        return (n >> 1) ^ -(n & 1)

    def readString(
        self, maximun: Optional[int] = None, encoding: Optional[str] = None
    ) -> str:
        return self.read(
            self.readVarInt()
            if maximun is None
            else min(self.readVarInt(), max(maximun, 0))
        ).decode(encoding or self.encoding)

    def readBytes(self, length: int) -> bytes:
        return self.read(length)

    def write(self, value: bytes | int):
        if isinstance(value, bytes):
            self.io.write(value)
        else:
            self.io.write((value + 256 if value < 0 else value).to_bytes(1, "big"))  # type: ignore

    def writeBoolean(self, value: bool):
        self.write(value.to_bytes(1, "big"))

    def writeShort(self, data: int):
        self.write(((data >> 8) & 0xFF).to_bytes(1, "big"))
        self.write(((data >> 0) & 0xFF).to_bytes(1, "big"))

    def writeInteger(self, data: int):
        self.write(((data >> 24) & 0xFF).to_bytes(1, "big"))
        self.write(((data >> 16) & 0xFF).to_bytes(1, "big"))
        self.write(((data >> 8) & 0xFF).to_bytes(1, "big"))
        self.write((data & 0xFF).to_bytes(1, "big"))

    def writeVarInt(self, value: int):
        self.write(Avro.getVarInt(value))

    def writeString(self, data: str, encoding: Optional[str] = None):
        self.writeVarInt(len(data.encode(encoding or self.encoding)))
        self.write(data.encode(encoding or self.encoding))

    def writeLong(self, data: int):
        data = data - 2**64 if data > 2**63 - 1 else data
        self.write((data >> 56) & 0xFF)
        self.write((data >> 48) & 0xFF)
        self.write((data >> 40) & 0xFF)
        self.write((data >> 32) & 0xFF)
        self.write((data >> 24) & 0xFF)
        self.write((data >> 16) & 0xFF)
        self.write((data >> 8) & 0xFF)
        self.write((data >> 0) & 0xFF)

    def __sizeof__(self) -> int:
        return self.io.tell()

    def __len__(self) -> int:
        return self.io.tell()

    @staticmethod
    def getVarInt(data: int):
        r: bytes = b""
        data = (data << 1) ^ (data >> 63)
        while (data & ~0x7F) != 0:
            r += ((data & 0x7F) | 0x80).to_bytes(1, "big")
            data >>= 7
        r += data.to_bytes(1, "big")
        return r


class WRRScheduler:
    def __init__(self):
        self.servers = {}
        self.queue = []

    def add_server(self, server, weight):
        # 添加服务器及其权重到字典
        self.servers[server] = weight
        # 向队列中添加多个条目，数量由权重决定
        for _ in range(weight):
            heapq.heappush(self.queue, (-weight, server))

    def remove_server(self, server):
        # 移除所有与指定服务器相关的条目
        self.queue = [item for item in self.queue if item[1] != server]
        # 从字典中删除服务器
        del self.servers[server]

    def update_weight(self, server, new_weight):
        # 移除所有与指定服务器相关的条目
        self.queue = [item for item in self.queue if item[1] != server]
        # 更新字典中的权重
        self.servers[server] = new_weight
        # 添加新的条目
        for _ in range(new_weight):
            heapq.heappush(self.queue, (-new_weight, server))

    def next_server(self):
        if not self.queue:
            return None
        # 弹出队列中的第一个元素
        weight, server = heapq.heappop(self.queue)
        # 将权重减一后重新插入队列
        heapq.heappush(self.queue, (weight + 1, server))
        return server


wrrs = WRRScheduler()
