from typing import List, Tuple, Type, Optional

from src.plugin_system import (
    BasePlugin,
    register_plugin,
    BaseCommand,
    ComponentInfo,
    ConfigField,
)

import pornhub


# ================== Pornhub 查询 Command ==================
class PornhubSearchCommand(BaseCommand):
    """
    用法：
    /ph 关键词
    """

    command_name = "pornhub_search"
    command_description = "根据关键词搜索Pornhub视频"

    command_pattern = r"^/ph\s+(?P<keyword>.+)$"

    async def execute(self) -> Tuple[bool, Optional[str], bool]:

        keyword = self.matched_groups.get("keyword")
        if not keyword:
            return False, "关键词不能为空", True

        try:
            # ===== 读取配置 =====
            use_proxy = self.get_config("pornhub.use_proxy", False)
            proxy_ip = self.get_config("pornhub.proxy_ip", "")
            proxy_port = self.get_config("pornhub.proxy_port", 0)
            result_limit = self.get_config("pornhub.result_limit", 5)

            # ===== 创建客户端 =====
            if use_proxy and proxy_ip and proxy_port:
                client = pornhub.PornHub(
                    keywords=[keyword],
                    ProxyIP=proxy_ip,
                    ProxyPort=proxy_port
                )
            else:
                client = pornhub.PornHub([keyword])

            # ===== 获取视频 =====
            videos = client.getVideos(result_limit)

            if not videos:
                await self.send_text(" 未找到相关视频")
                return True, "无结果", True

            # ===== 构建返回 =====
            msg = f" Pornhub 搜索结果：{keyword}\n\n"

            for i, v in enumerate(videos, 1):
                title = v.get("title", "无标题")
                url = v.get("url", "")

                msg += f"{i}. {title}\n{url}\n\n"

            await self.send_text(msg)
            return True, f"查询成功: {keyword}", True

        except Exception as e:
            await self.send_text(" 查询失败（网络/代理/API异常）")
            return False, str(e), True


# ================== 插件主类 ==================
@register_plugin
class HelloWorldPlugin(BasePlugin):
    """Pornhub 查询插件"""

    plugin_name = "pornhub_query_plugin"
    enable_plugin = True
    dependencies = []
    python_dependencies = ["pornhubapi"]
    config_file_name = "config.toml"

    # ===== 配置 Schema =====
    config_schema = {
        "pornhub": {
            "use_proxy": ConfigField(
                type=bool,
                default=False,
                description="是否使用代理"
            ),
            "proxy_ip": ConfigField(
                type=str,
                default="",
                description="代理IP"
            ),
            "proxy_port": ConfigField(
                type=int,
                default=0,
                description="代理端口"
            ),
            "result_limit": ConfigField(
                type=int,
                default=5,
                description="返回视频数量"
            ),
        }
    }

    def get_plugin_components(self) -> List[Tuple[ComponentInfo, Type]]:
        return [
            (PornhubSearchCommand.get_command_info(), PornhubSearchCommand),
        ]