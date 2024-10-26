# 第三方库
import yaml
from pathlib import Path

# 本地库
from core.logger import logger

class Config:
    def __init__(self, config_file):
        self.config_file = config_file
        self.config = self.load_config()

    def load_config(self):
        with open(self.config_file, "r", encoding="utf-8") as file:
            config = yaml.safe_load(file)
        return config

    def get(self, path: str, default = None):
        keys = path.split(".")
        data = self.config
        try:
            for key in keys:
                data = data[key]
            return data
        except (KeyError, TypeError):
            logger.warning(f"{path} 未设置，已返回 None 作为默认值。")
            return default


config = Config(Path("./config.yml"))