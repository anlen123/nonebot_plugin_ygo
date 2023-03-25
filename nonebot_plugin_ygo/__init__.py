import aiohttp
import nonebot
from nonebot.plugin import on_regex
from nonebot.adapters.onebot.v11 import Bot, Event, Message, MessageSegment, GroupMessageEvent,PrivateMessageEvent
import re
import os
from nonebot.rule import to_me
import math


global_config = nonebot.get_driver().config
config = global_config.dict()

ygo_max = int(config.get("ygo_max",5))
ygo_cmd = str(config.get("ygo_cmd", "ygo"))

ygo = on_regex(pattern="^{}\ ".format(ygo_cmd))


@ygo.handle()
async def ygoMethod(bot: Bot, event: Event):
    raw_msg = str(event.message)
    info = raw_msg.split(' ')
    if len(info) == 2:
        start, end = 0, ygo_max
        num = 1
    elif len(info) == 3:
        try:
            num = int(info[2])
            if num < 1:
                await bot.send(event=event,message = "页码不能小于1")  
                await ygo.finish()
        except ValueError:
            await bot.send(event=event,message = "应当输入页码")
            await ygo.finish()
        start, end = (num-1)*ygo_max, num*ygo_max
    else:
        await bot.send(event=event,message = "未输入关键字或关键字过多")
        await ygo.finish()

    key = info[1]
    total_img = await main(key)
    imgs = total_img[start:end]
    msg = None
    for img in imgs:
        msg += MessageSegment.image(img)
    total_page = math.ceil(len(total_img)/ygo_max)
    if num == total_page:
        msg += MessageSegment.text('当前第{}页, 共{}页。'.format(num, total_page))
    elif num < total_page:
        msg += MessageSegment.text('当前第{}页, 共{}页。输入【卡查 {} {}】查看下一页'.format(num, total_page, key, num+1))
    if isinstance(event,GroupMessageEvent):
        await send_forward_msg_group(bot, event, "ygo卡查", msg if msg else ["没有此关键字的卡片"])
    elif isinstance(event,PrivateMessageEvent):
        await bot.send(event=event,message = msg if msg else "没有此关键字的卡片")
    await ygo.finish()



async def main(key: str):
    url = f"https://ygocdb.com/?search={key}"
    headers = {
        'user-agent': 'nonebot-plugin-ygo',
        'referer': 'https://ygocdb.com/',
    }
    imgs = []
    async with aiohttp.ClientSession() as session:
        c = await session.get(url=url, headers=headers)
        text = (await c.content.read()).decode()
        imgs = re.findall('<img data-original="(.*?)!half">', text)
    return imgs


# 合并消息
async def send_forward_msg_group(
        bot: Bot,
        event: GroupMessageEvent,
        name: str,
        msgs: [],
):
    def to_json(msg):
        return {"type": "node", "data": {"name": name, "uin": bot.self_id, "content": msg}}

    messages = [to_json(msg) for msg in msgs]
    await bot.call_api(
        "send_group_forward_msg", group_id=event.group_id, messages=messages
    )