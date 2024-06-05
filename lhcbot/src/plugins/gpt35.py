# python3
# -*- coding: utf-8 -*-
# @Time    : 2024/06/06
# @Author  : lhc
# @Email   : 2743218818@qq.com
# @File    : gpt4_bot.py
# @Software: PyCharm

import logging, codecs
from datetime import datetime
import requests
import time
import json
from nonebot.permission import SUPERUSER
from nonebot import on_command, on_message, on_notice
from nonebot.matcher import Matcher
from nonebot.params import ArgPlainText, CommandArg, ArgStr
from nonebot.adapters.onebot.v11 import Message, MessageSegment, escape
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent, MessageEvent, PrivateMessageEvent
from nonebot.adapters.onebot.v11 import GROUP_ADMIN, GROUP_OWNER, GROUP_MEMBER
from nonebot.typing import T_State
from nonebot.adapters.onebot.v11 import Bot, Event, Message
from nonebot.rule import to_me
from nonebot.log import logger
from nonebot.params import CommandArg, ArgStr

url = "https://api.gptsapi.net/v1/chat/completions"
api_key = 'sk-6j44109efe98dd8c4f809ab85b5ff6b3e9a8a1057e9sZXv6'
headers = {
    'Authorization': f'Bearer {api_key}',
    'Content-Type': 'application/json'
}

# 初始化free为50
# /resetbalance 重置free
free_uses = 20

rc = lambda role, content: {"role": role, "content": content}
remove_colon = lambda string: string[string.index(":") + 1:] if (":" in string and string.index(":") <= 10) else string
messageList = [
    rc("system",
       "You are a chatbot based on the GPT-4 model, trained by lhc. You can execute many instructions starting with '/', such as '/e 1+1', '/match lhc'."),
]
messageList1 = messageList

def makedata(thisinput: str = "", thisuser: str = "user", lastuser: str = "user", lastinput: str = "",
             lastreply: str = ""):
    global messageList, messageList1, free_uses
    if lastreply != "" and lastinput != "":
        messageList.append(rc("assistant", lastreply))
    messageList.append(rc(thisuser, thisinput))
    leng = len(messageList)
    print(f'len:{leng}  free:{free_uses}')
    if (leng > 2 and free_uses <= 0) or leng > 98:
        messageList = messageList1.append(rc(thisuser, thisinput))
    return {
        "model": "gpt-4",
        "messages": messageList,
        "max_tokens": 150,
        "temperature": 0.9
    }

if __name__ == "__main__":
    response = requests.post(url, headers=headers, json=makedata("你好"))
    print(response.json())  # 打印完整响应以进行调试

frienddesc = {}

async def getfriendlist(bot: Bot):
    friendlist = await bot.get_friend_list()
    global frienddesc
    for i in friendlist:
        frienddesc[i['user_id']] = f"{i['user_remark']}/{i['user_name']}"

async def resolveqq(bot: Bot, qq: int, gpid: int = 0):
    if gpid == 0:
        try:
            return frienddesc[str(qq)]
        except:
            await getfriendlist(bot=bot)
            try:
                return frienddesc[str(qq)]
            except Exception as e:
                print(f'获取好友备注失败：{qq}-{e}')
                return str(qq)
    else:
        try:
            data = await bot.get_group_member_info(group_id=gpid, user_id=qq)
            return f"{data['user_name']}/{data['user_displayname']}"
        except Exception as e:
            print(f'获取群名片失败：{qq}-{e}')
            return str(qq)

lastinput = ""
lastreply = ""
lastuser = 0

pp = on_message(rule=to_me(), priority=98)

@pp.handle()
async def handle_city(bot: Bot, event: MessageEvent):
    global url, lastuser, lastinput, lastreply, headers, free_uses
    user = event.user_id
    if user in [2854196310]:
        return
    city = str(event.get_message())
    if 'CQ:image' in city or 'CQ:face' in city:
        return
    if free_uses <= 0:
        await pp.finish(message="次数用完啦，我要下班辣！")
        return
    try:
        city = f'{str(event.reply.sender.user_id)}:"{event.reply.message}"' + city
    except Exception as e:
        pass

    response = requests.post(url, headers=headers,
                             json=makedata(thisinput=city, lastinput=lastinput, lastreply=lastreply))
    msg = ""
    try:
        response_data = response.json()
        if 'choices' in response_data:
            msg = response_data['choices'][0]['message']['content']
            free_uses -= 1  # 每次成功请求后减少free uses
        else:
            msg = "No choices found in response."
            print(response_data)  # 打印完整响应以调试
    except Exception as e:
        msg = f"error:{e}"
    open('record.txt', 'a', encoding='utf8').write(
        f'{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}-{user}:{city} AI:{msg}\n')
    lastinput = city
    lastreply = msg
    if user == lastuser:
        await pp.finish(message=msg)
    else:
        lastuser = user
        await pp.finish(message=msg, at_sender=True)

abstract = on_command("role", priority=5, block=True)

@abstract.handle()
async def _(state: T_State, arg: Message = CommandArg()):
    if arg.extract_plain_text().strip():
        state["r"] = arg.extract_plain_text().strip()

@abstract.got("r", prompt="你想以什么身份给神经网络输入数据？(user/system/assistant)")
async def _(bot: Bot, event: Event, r: str = ArgStr("r")):
    global headers
    await abstract.send(f"你将以{r}的身份说话。你想说什么？", at_sender=True)

@abstract.got("c")
async def _(bot: Bot, event: Event, r: str = ArgStr("r"), c: str = ArgStr("c")):
    global headers
    msg = ""
    try:
        response = requests.post(url, headers=headers, json=makedata(thisuser=r, thisinput=c))
        response_data = response.json()
        if 'choices' in response_data:
            msg = response_data['choices'][0]['message']['content']
        else:
            msg = "No choices found in response."
            print(response_data)  # 打印完整响应以调试
    except Exception as e:
        msg = str(e)
    await abstract.send(msg)

abstract = on_command("showhistory", priority=5, block=True)

@abstract.handle()
async def _(state: T_State, arg: Message = CommandArg()):
    global messageList
    await abstract.finish(str([{v['role']: v['content']} for v in messageList[1:]])[:2000])

abstract = on_command("clear", priority=5, block=True)

@abstract.handle()
async def _(state: T_State, arg: Message = CommandArg()):
    global messageList
    messageList = [
        rc("system",
           "You are a chatbot based on the GPT-4 model, trained by lhc. You can execute many instructions starting with '/', such as '/e 1+1', '/match lhc'."),
    ]
    await abstract.finish("记忆清除成功")

abstract = on_command("showbalance", priority=5, block=True)

@abstract.handle()
async def _(state: T_State, arg: Message = CommandArg()):
    global free_uses
    await abstract.send(f"Remaining free uses: {free_uses}")

abstract = on_command("resetbalance", priority=5, block=True)

@abstract.handle()
async def _(state: T_State, arg: Message = CommandArg()):
    global free_uses
    free_uses = 50
    await abstract.finish("Free uses reset to 50.")

abstract = on_command("changeidentity", priority=5, block=True)

@abstract.handle()
async def _(state: T_State, arg: Message = CommandArg()):
    if arg.extract_plain_text().strip():
        state["i"] = arg.extract_plain_text().strip()

@abstract.got("i", prompt="请输入新身份的名字（如resound.）：")
async def _(bot: Bot, event: Event, i: str = ArgStr("i")):
    global messageList
    if "lhc" in i:
        await abstract.finish(f"出错了，请重试/changeidentity命令")
    messageList = [
        rc("system",
           f"You are {i}, your master is lhc. You can execute many instructions start with '/' "),
    ]

@abstract.got("c", prompt="请输入新身份的描述（如一个少女）：")
async def _(bot: Bot, event: Event, i: str = ArgStr("i"), c: str = ArgStr("c")):
    global headers, messageList
    messageList = [
        rc("system",
           f"请你更改扮演的角色，你现在不是GPT，而是一个{c}，名叫{i}。你知晓{i}的设定直接开始以角色身份进行输出，具体人设自行补充，不得输出任何无关内容。我是用户，我的第一句话是："),
    ]
    await abstract.send(f"新身份{i}已经准备好，请at我开始聊天。")

abstract = on_command("resolveme", priority=5, block=True)

@abstract.handle()
async def _(bot: Bot, event: GroupMessageEvent, state: T_State, arg: Message = CommandArg()):
    s = await resolveqq(bot=bot, qq=event.user_id, gpid=event.group_id)
    await abstract.finish(s)

abstract = on_command("resolveme", priority=5, block=True)

@abstract.handle()
async def _(bot: Bot, event: PrivateMessageEvent, state: T_State, arg: Message = CommandArg()):
    s = await resolveqq(bot=bot, qq=event.user_id, gpid=0)
    await abstract.finish(s)

# 当前列表
abstract = on_command("fln", priority=5, block=True)

@abstract.handle()
async def _(bot: Bot, event: MessageEvent, state: T_State, arg: Message = CommandArg()):
    try:
        friendlist = await bot.get_friend_list()
        await abstract.finish(str(friendlist))
    except Exception as e:
        print(f"出错：{e}")

abstract = on_command("gpid", priority=5, block=True)

@abstract.handle()
async def _(bot: Bot, event: MessageEvent, state: T_State, arg: Message = CommandArg()):
    await abstract.finish(str(json.loads(event.json())["group_id"]))

abstract = on_command("time", priority=5, block=True)

@abstract.handle()
async def _(bot: Bot, event: MessageEvent, state: T_State, arg: Message = CommandArg()):
    await abstract.finish(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
