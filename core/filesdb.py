import os
import atexit
import asyncio
import aiosqlite


class FilesDB:
    def __init__(self):
        self.conn = None
        self.cursor = None

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def connect(self):
        if not os.path.exists("./data/database.db"):
            raise FileNotFoundError("数据库文件不存在")
        self.conn = await aiosqlite.connect("./data/database.db")
        self.cursor = await self.conn.cursor()

    async def close(self):
        if self.conn:
            await self.conn.close()
        self.conn = None
        self.cursor = None

    async def create_table(self):
        await self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS FILELIST
            (
                HASH TEXT PRIMARY KEY,
                PATH TEXT,
                URL TEXT,
                SIZE INTEGER,
                MTIME INTEGER,
                SOURCE TEXT
            )
        """
        )
        await self.conn.commit()
        await self.close()

    async def new_file(
        self,
        hash: str,
        path: str = "",
        url: str = "",
        size: int = 0,
        mtime: int = 0,
        source: str = "local",
    ):
        await self.connect()
        await self.conn.execute(
            """
            INSERT INTO FILELIST (
                HASH,
                PATH,
                URL,
                SIZE,
                MTIME,
                SOURCE
            ) VALUES (?, ?, ?, ?, ?, ?)
        """,
            (
                hash,
                path,
                url,
                size,
                mtime,
                source,
            ),
        )
        await self.conn.commit()
        return True

    async def delete_file(self, hash: str):
        await self.conn.execute(
            """
            DELETE FROM FILELIST WHERE HASH = ?
        """,
            (hash,),
        )
        await self.conn.commit()
        return True

    async def delete_all(self):
        await self.conn.execute(
            """
            DELETE FROM FILELIST
        """,
        )
        await self.conn.commit()
        return True

    async def find_one(self, key: str, value: str):
        async with self.conn.execute(
            f"""
            SELECT * FROM FILELIST WHERE {key} = ?
        """,
            (value,),
        ) as cursor:
            row = await cursor.fetchone()
            if row:
                columns = [desc[0] for desc in cursor.description]
                result = dict(zip(columns, row))
            else:
                result = False
        return result

    async def get_all(self):
        async with self.conn.execute("SELECT * FROM FILELIST") as cursor:
            rows = await cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            result = [dict(zip(columns, row)) for row in rows]
        return result