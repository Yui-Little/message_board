from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star, register
from astrbot.api import logger
import os
from datetime import datetime

@register("message_board", "YuiLittle", "一个用于记录群聊留言的插件", "1.0.0", "")
class MessageLoggerPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)
        self.file_path = os.path.join("data", "plugins", "message_board", "留言.txt")
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
        self.admin_qq = "你的QQ"

    @filter.command("留言")
    async def log_message(self, event: AstrMessageEvent, content: str):
        """
        命令格式：/留言 内容
        """
        try:
            sender_id = event.get_sender_id()
            sender_name = event.get_sender_name()
            group_id = event.get_group_id()
            timestamp = datetime.now().strftime("%Y年%m月%d日 %H时%M分%S秒")
            
            if group_id:  
                log_entry = (
                    f"时间: {timestamp}\n"
                    f"群聊号码: {group_id}\n"
                    f"用户QQ: {sender_id}\n"
                    f"用户名字: {sender_name}\n"
                    f"留言内容: {content}\n"
                    f"状态: 未解决\n"
                    "------------------------\n"
                )
            else:  
                log_entry = (
                    f"时间: {timestamp}\n"
                    f"用户QQ: {sender_id}\n"
                    f"用户名字: {sender_name}\n"
                    f"留言内容: {content}\n"
                    f"状态: 未解决\n"
                    "------------------------\n"
                )

            with open(self.file_path, "a", encoding="utf-8") as f:
                f.write(log_entry)

            logger.info(f"已记录留言，用户: {sender_name} ({sender_id}), 内容: {content}")

            if event.get_platform_name() == "aiocqhttp":
                from astrbot.core.platform.sources.aiocqhttp.aiocqhttp_message_event import AiocqhttpMessageEvent
                if isinstance(event, AiocqhttpMessageEvent):
                    client = event.bot
                    await client.api.call_action(
                        'send_private_msg',
                        user_id=int(self.admin_qq),
                        message=f"你收到一条新的留言，请前往 {self.file_path} 查看"
                    )
                    logger.info(f"已通过 API 向管理员 {self.admin_qq} 发送通知")
                else:
                    logger.error("事件类型不匹配，无法获取 aiocqhttp 客户端")
                    yield event.plain_result("记录留言成功，但通知管理员失败。")
            else:
                logger.error("当前平台不是 aiocqhttp，无法发送通知")
                yield event.plain_result("记录留言成功，但通知管理员失败。")

            yield event.plain_result("你的留言已记录，管理员会尽快处理。")

        except Exception as e:
            logger.error(f"记录留言时发生错误: {str(e)}")
            yield event.plain_result("记录留言失败，请稍后再试或联系管理员。")

    async def terminate(self):
        """
        插件卸载时的清理工作，此处无特殊资源需要释放。
        """
        logger.info("留言记录插件已卸载")
