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
        'authority': 'ygocdb.com',
        'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="98", "Google Chrome";v="98"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-user': '?1',
        'sec-fetch-dest': 'document',
        'referer': 'https://ygocdb.com/',
        'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8'
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
