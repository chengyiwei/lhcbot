# python3
# -*- coding: utf-8 -*-
# @Time    : 2023/11/27
# @Author  : lhc
# @Email   : 2743218818@qq.com
# @File    : gpt35.py
# @Software: PyCharm
# @Url     : https://x.dogenet.win?aff=VqY0cguY
# 1跟着上个视频教程搭好机器人
# 2获取本文件
# 3获取auth和sess
# 4把本文件放到插件目录
import logging, codecs
from datetime import datetime
import requests
import time
import json
from nonebot.permission import SUPERUSER
from nonebot import on_command, on_startswith, on_keyword, on_fullmatch, on_message, on_notice
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

url = "https://x.dogenet.win/api/v1/ai/chatgpt/chat"
headers = {
    'Accept': 'application/json, text/plain, */*',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Authorization': 'Bearer eyJhbGciOiJFUzUxMiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjM1MjY3IiwiZW1haWwiOiJjeXcxNDhAZ21haWwuY29tIiwicHVycG9zZSI6IndlYiIsImlhdCI6MTcxNjAxNjUwNywiZXhwIjoxNzE3MjI2MTA3fQ.AdZl4BzwY7599-Z-cBLfVCMvjZ-DjM6vurNRm1VzyejC2fOx5UVpTJE0GespP7MHuv2RnUddSTLovskZ5DwXj7CLADqisxxKqDiKY1vUaqYXW3G-jnS1robux6iofOXGCX_sHyFFb5OwfhDZNZdpomg5PZvPmI2IonX2P9g2oiwztx6j',  # 改左边
    'Cache-Control': 'no-cache',
    'Cookie': '_ga=GA1.1.576617952.1697654108; _ga_5C4RB337FM=GS1.1.1697654108.1.1.1697655679.0.0.0',
    'Origin': 'https://x.dogenet.win',
    'Pragma': 'no-cache',
    'Referer': 'https://x.dogenet.win/pay',
    'Sec-Ch-Ua': '"Chromium";v="118", "Microsoft Edge";v="118", "Not=A?Brand";v="99"',
    'Sec-Ch-Ua-Mobile': '?0',
    'Sec-Ch-Ua-Platform': '"Windows"',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36 Edg/118.0.2088.46'
}

rc = lambda role, content: {"role": role, "content": content}
remove_colon = lambda string: string[string.index(":") + 1:] if (":" in string and string.index(":") <= 10) else string
messageList = [
    rc("system",
       "You are resound., a chat robot trained by Martian148,you can execute many instructions start with '/', such as '/e 1+1','/匹配 Martian148'"),
]
messageList1 = messageList

def makedata(thisinput: str = "", thisuser: str = "user", lastuser: str = "user", lastinput: str = "",
             lastreply: str = ""):
    global messageList, messageList1
    if lastreply != "" and lastinput != "":
        # messageList.append(rc(lastuser, lastinput))
        messageList.append(rc("assistant", lastreply))
    messageList.append(rc(thisuser, thisinput))
    try:
        free = getBalance()['free_balance']
    except Exception as e:
        free = str(e)
    leng = len(messageList)
    print(f'len:{leng}  free:{free}')
    try:
        if (leng > 2 and float(free) < 10) or leng > 98:
            messageList = messageList1.append(rc(thisuser, thisinput))
    except ValueError:
        messageList = [rc(thisuser, thisinput)]
    return {
        "session_id": "a558f190-da30-4558-8861-2fd7ff510c2c",  # 改左边
        "content": json.dumps(messageList),
        "max_context_length": "5",
        "params": json.dumps({
            "model": "gpt-3.5-turbo",
            "temperature": 1,
            "max_tokens": 2048,
            "presence_penalty": 0,
            "frequency_penalty": 0,
            "max_context_length": 5,
            "voiceShortName": "zh-CN-XiaoxiaoNeural",
            "rate": 1,
            "pitch": 1
        })
    }


def getBalance():
    global headers
    url1 = 'https://x.dogenet.win/api/v1/user/balance'
    response = requests.post(url1, headers=headers).json()
    # print('余额', response['data']['balance'])
    # print('免费', response['data']['free_balance'])
    return response['data']


if __name__ == "__main__":
    response = requests.post(url, headers=headers, data=makedata("你好"), stream=True)

    for line in response.iter_lines():
        if line:
            text = line.decode("utf-8")  # 将字节流解码为文本
            print(text)  # 打印每行文本数据

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
    global url, lastuser, lastinput, lastreply, headers
    user = event.user_id
    if user in [2854196310]:
        return
    city = str(event.get_message())
    if 'CQ:image' in city or 'CQ:face' in city:
        return
    # try:
    #     userinfo = await resolveqq(bot=bot, qq=user, gpid=json.loads(event.json())["group_id"])
    # except:
    #     userinfo = await resolveqq(bot=bot, qq=user, gpid=0)
    # city = f'{userinfo}:' + city
    try:
        city = f'{str(event.reply.sender.user_id)}:"{event.reply.message}"' + city
    except Exception as e:
        pass

    response = requests.post(url, headers=headers,
                             data=makedata(thisinput=city, lastinput=lastinput, lastreply=lastreply),
                             stream=True)
    msg = ""
    try:
        decoder = codecs.getincrementaldecoder('utf-8')()
        for chunk in response.iter_content(chunk_size=1):
            try:
                decoded_chunk = decoder.decode(chunk, final=False)
                print(decoded_chunk, end='')
                msg += decoded_chunk
            except UnicodeDecodeError:
                pass  # 解码错误，继续等待后续数据到达
        msg = msg[:-6]
        # msg = remove_colon(msg)
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
        r = requests.post(url, headers=headers, data=makedata(thisuser=r, thisinput=c), stream=True)
        try:
            ls = []
            for line in r.iter_lines():
                if line:
                    text = line.decode("utf-8")  # 将字节流解码为文本
                    print(text)  # 打印每行文本数据
                    ls.append(text)
                msg = '\n'.join(ls)
                print(msg)
        except:
            msg = r.text
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
           "You are resound., a chat robot trained by Martian148,you can execute many instructions start with '/', such as '/e 1+1','/匹配 Martian148'"),
    ]
    await abstract.finish("记忆清除成功")


abstract = on_command("showbalance", priority=5, block=True)


@abstract.handle()
async def _(state: T_State, arg: Message = CommandArg()):
    global headers
    url1 = 'https://x.dogenet.win/api/v1/user/balance'
    url2 = 'https://x.dogenet.win/api/v1/pay/statistics/model-usage-by-day'
    # 将日期转换为字符串
    date_str = datetime.now().date().strftime("%Y-%m-%d")
    # 构建请求负载
    payload = {
        "date": date_str,
        "timeZone": "Asia/Shanghai"
    }
    response = requests.post(url1, headers=headers).json()
    await abstract.send(str(response))
    print(response)
    response = requests.post(url2, headers=headers, json=payload).json()
    print(response)
    await abstract.finish(str(response))


abstract = on_command("changeidentity", priority=5, block=True)


@abstract.handle()
async def _(state: T_State, arg: Message = CommandArg()):
    if arg.extract_plain_text().strip():
        state["i"] = arg.extract_plain_text().strip()


@abstract.got("i", prompt="请输入新身份的名字（如resound.）：")
async def _(bot: Bot, event: Event, i: str = ArgStr("i")):
    global messageList
    if "Martian148" in i:
        await abstract.finish(f"出错了，请重试/changeidentity命令")
    messageList = [
        rc("system",
           f"You are {i},your master is Martian148.You can execute many instructions start with '/' "),
    ]


@abstract.got("c", prompt="请输入新身份的描述（如一个少女）：")
async def _(bot: Bot, event: Event, i: str = ArgStr("i"), c: str = ArgStr("c")):
    global headers, messageList
    messageList = [
        rc("system",
           f"请你更改扮演的角色，你现在不是GPT，而是一个{c}，名叫{i}。你知晓{i}的设定直接开始以角色身份进行输出，具体人设自行补充，不得输出任何无关内容.我是用户，我的第一句话是："),
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
