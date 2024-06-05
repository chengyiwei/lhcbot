import nonebot
from nonebot import on_command
from nonebot.adapters.onebot.v11 import Bot, MessageEvent, MessageSegment
from .calculate_rating import rating  # 假设 rating.py 中有一个名为 QQ_ask 的函数

# 创建命令处理器，监听 "cf" 命令
cf_command = on_command("cf", aliases={"at", "rating", "contest", "c", "help", "stu", "info"}, priority=4)

# 定义处理函数
@cf_command.handle()
async def handle_cf(bot: Bot, event: MessageEvent):
    message_text = event.get_plaintext()
    result = rating.QQ_ask(message_text)  # 正确调用 QQ_ask 函数
    if result == "error":
        await bot.send(event, MessageSegment.text("输入错误，请重新输入"))
    else:
        await bot.send(event, MessageSegment.text(result))