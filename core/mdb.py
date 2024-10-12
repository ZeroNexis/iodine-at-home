# 第三方库
import motor.motor_asyncio
from bson.objectid import ObjectId

# 本地库
from core.config import config


def to_objectId(id: str):
    try:
        return ObjectId(id)
    except Exception:
        return None


class Database:
    def __init__(
        self,
        url: str,
        db_name: str,
        collection_name: str,
        username=None,
        password=None,
    ):
        uri = (
            f"mongodb://{username}:{password or ''}@{url}/"
            if username
            else f"mongodb://{url}/"
        )
        self.client = motor.motor_asyncio.AsyncIOMotorClient(uri)
        self.db = self.client[db_name]
        self.collection_name = collection_name

    async def close(self):
        self.client.close()

    async def collection(self, collection_name: str):
        return self.db[collection_name]

    async def insert_one(self, data: dict):
        collection = await self.collection(self.collection_name)
        result = await collection.insert_one(data)
        return result.inserted_id

    async def find_one(self, query: dict):
        collection = await self.collection(self.collection_name)
        return await collection.find_one(query)

    async def create_cluster(
        self,
        name: str = None,
        secret: str = None,
        bandwidth: int = None,
    ):
        return await self.insert_one(
            {
                "name": name,
                "secret": secret,
                "bandwidth": bandwidth,
                "isBanned": False
            }
        )

    async def delete_cluster(self, id: str):
        collection = await self.collection(self.collection_name)
        await collection.delete_one({"_id": to_objectId(id)})

    async def find_cluster(self, id: str):
        collection = await self.collection(self.collection_name)
        result = await collection.find_one({"_id": to_objectId(id)})
        if result:
            return [True, result]
        return [False, None]

    async def get_all(self):
        collection = await self.collection(self.collection_name)
        cursor = collection.find()
        return [doc async for doc in cursor]

    async def edit_cluster(
        self,
        id: str,
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
        cert_expiry: str = None
    ):
        data = {
            "name": name,
            "secret": secret,
            "bandwidth": bandwidth,
            "measureBandwidth": measureBandwidth,
            "trust": trust,
            "isBanned": isBanned,
            "ban_reason": ban_reason,
            "host": host,
            "port": port,
            "version": version,
            "runtime": runtime,
            "cert_fullchain": cert_fullchain,
            "cert_privkey": cert_privkey,
            "cert_expiry": cert_expiry
        }
        valid_update_data = {k: v for k, v in data.items() if v is not None}
        result = await self.db.clusters.update_one(
            {"_id": to_objectId(id)},
            {"$set": valid_update_data},
        )
        if result.modified_count == 1:
            return True
        return False


cdb = Database(
    config.get("mongodb.url"),
    config.get("mongodb.db_name"),
    "clusters",
    config.get("mongodb.username"),
    config.get("mongodb.password"),
)