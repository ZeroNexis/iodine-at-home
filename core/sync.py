from git.repo import Repo
from core.config import config
import os
import hashlib
download_path = os.path.join(config.get('download_path'))

Repo.clone_from(url=config.get('git_repo.url'),to_path=download_path,branch=config.get('git_repo.branch'))


async def generate_filelist():
    global file_list
    file_list = []
    for root, dirs, files in os.walk(config.get('download_path')):
        for file in files:
            file_path = os.path.join(root, file)
            file_hash = get_file_hash(file_path)
            file_entry = {
                "_hash": file_hash,
                "path": file_path,
                "name": file
            }
            file_list.append(file_entry)
    return file_list

async def get_file_hash(file_path):
    hash_md5 = hashlib.md5()
    with open (file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

# async def write_to_db():
#     for i in file_list:
#         await fdb.file.insert_one(i)