import aiohttp
import nonebot
from nonebot.plugin import on_regex
from nonebot.adapters.onebot.v11 import Bot, Event, Message, MessageSegment, GroupMessageEvent,PrivateMessageEvent
import re
import os

global_config = nonebot.get_driver().config
config = global_config.dict()

ygo_max = int(config.get("ygo_max",10))

ygo = on_regex(pattern="^ygo\ ")


@ygo.handle()
async def ygoMethod(bot: Bot, event: Event):
    key = str(event.message).strip()[3:].strip()
    imgs = (await main(key))[:ygo_max]
    msg = None
    for img in imgs:
        msg += MessageSegment.image(img)
    if isinstance(event,GroupMessageEvent):
        await send_forward_msg_group(bot, event, "qqbot", msg if msg else ["没有此关键字的卡片"])
    elif isinstance(event,PrivateMessageEvent):
        await bot.send(event=event,message = msg if msg else "没有此关键字的卡片")



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
