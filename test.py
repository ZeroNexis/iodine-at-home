import tqdm

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
                return hash, self.size_list[self.hash_list.index(hash)], self.mtime_list[self.hash_list.index(hash)], self.url_list[self.hash_list.index(hash)],
            else:
                return None, None, None, None
        elif url is not None:
            if url in self.url_list:
                return self.size_list[self.url_list.index(url)], self.mtime_list[self.url_list.index(url)], self.hash_list[self.url_list.index(url)], url
            else:
                return None, None, None, None
        else:
            return None, None, None, None
        
filesdb = FilesDB()

for i in tqdm.tqdm(range(1000)):
    filesdb.append(f"hash{i}", i, i, f"url{i}")

print(filesdb.find(url="url500"))