from pluginbase import PluginBase
from loguru import logger
import asyncio
plugin_base = PluginBase(package='iodine.plugins')
plugin_source = plugin_base.make_plugin_source(searchpath=['./plugins'])

async def load_plugins():
    for plugin_name in plugin_source.list_plugins():
        plugin = plugin_source.load_plugin(plugin_name)
        logger.info(f"加载插件: {plugin_name}")
        asyncio.run(plugin.init())