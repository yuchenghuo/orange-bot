import asyncio
import json
import os
import random
import time
from datetime import date, timedelta
from typing import Optional, Union

from dotenv import load_dotenv
from requests import request
from wechaty import Wechaty, Contact
from wechaty.user import Message, Room
from wechaty_puppet import FileBox, EventReadyPayload  # type: ignore

load_dotenv()
wallets = {
    "example_user": {
        "coin": 0,
        "relation": 0,
        "上次签到": str(date.today()),
    },
} if not os.path.exists("wallet.json") \
    else json.load(open("wallet.json"))
streams = [] if not os.path.exists("streams.json") \
    else json.load(open("streams.json"))
TOKEN = os.getenv("SALMON_API_TOKEN")
CHAT_PLATFORM = "微信"
DRAW_LOTS = {
    '周易': 'zhouyi',
    '塔罗': 'tarot',
    '阴阳师签': 'yys',
    '观音签': 'guanyin',
    '喷喷运势': 'splatoon2',
    '诸葛签': 'zhuge',
    '诸葛签详解': 'zhuge/detail',
    '狒狒运势': 'ff14',
    '怪猎运势': 'monster_hunter',
}
zodiacs = {'白羊座', '金牛座', '双子座', '巨蟹座', '狮子座', '处女座',
           '天秤座', '天蝎座', '射手座', '摩羯座', '水瓶座', '双鱼座'}


class OrangeBot(Wechaty):

    async def heartbeat(self):
        while True:
            # Load the wechat_id of the bot account itself,
            # modify the following line to fit your own bot
            contact = self.Contact.load('wxid_gnb3cyngpude12')
            await contact.say('🍊')
            time.sleep(30)

    async def on_ready(self, payload: EventReadyPayload) -> None:
        asyncio.create_task(self.heartbeat())

    async def on_message(self, msg: Message):
        """
        listen for message event
        """
        from_contact: Optional[Contact] = msg.talker()
        text = msg.text()
        room: Optional[Room] = msg.room()
        conversation: Union[
            Room, Contact] = from_contact if room is None else room
        await conversation.ready()
        for i, (uid, room_id, reminded) in enumerate(streams):
            url = "http://api.live.bilibili.com/room/" \
                  "v1/Room/get_status_info_by_uids?uids[]=" + uid
            r = request('GET', url)
            data = r.json()['data'][uid]
            if data['live_status'] == 1:
                if not reminded:
                    remind_room = self.Room.load(room_id)
                    await remind_room.ready()
                    await remind_room.say(
                        f"关注的主播{data['uname']}直播开始了，快来看看吧！"
                        f"\n直播标题：{data['title']}"
                        f"\n直播链接：https://live.bilibili.com/{data['room_id']}"
                    )
                    streams[i][2] = True
            elif reminded:
                remind_room = self.Room.load(room_id)
                await remind_room.ready()
                await remind_room.say(
                    f"关注的主播{data['uname']}直播结束了！"
                )
                streams[i][2] = False
        if text in DRAW_LOTS.keys():
            url = f'https://api.salmoncross.xyz/v1/draw_lots/{DRAW_LOTS[text]}'
            r = request('GET', url,
                        params={
                            "token": TOKEN,
                            "user_id": from_contact.get_id(),
                            "chat_platform": CHAT_PLATFORM,
                        })
            if text == '塔罗':
                await conversation.say(
                    f"\n{r.json()['data']['content']}", [from_contact.get_id()]
                )
            elif text == '观音签':
                reply = FileBox.from_url(r.json()['data'], 'reply.png')
                await conversation.say(reply)
            else:
                await conversation.say(
                    f"\n{r.json()['data']}", [from_contact.get_id()]
                )
        elif text == '签到':
            reward = random.randint(0, 30)
            if from_contact.get_id() not in wallets.keys():
                wallets[from_contact.get_id()] = {
                    "coin": 0,
                    "relation": 0,
                    "上次签到": str(date.today() - timedelta(days=1)),
                }
            if wallets[from_contact.get_id()]['上次签到'] != str(date.today()):
                wallets[from_contact.get_id()]['coin'] += reward
                wallets[from_contact.get_id()]['relation'] += 1
                wallets[from_contact.get_id()]['上次签到'] = str(date.today())
                await conversation.say(
                    f'\n签到成功！'
                    f'\n获得了{reward}🍊'
                    f'\n当前🍊：{wallets[from_contact.get_id()]["coin"]}🍊'
                    f'\n亲密度：{wallets[from_contact.get_id()]["relation"]}',
                    [from_contact.get_id()])
                with open('wallet.json', 'w', encoding='utf-8') as f:
                    json.dump(wallets, f, ensure_ascii=False, indent=4)
            else:
                await conversation.say(f'你今天已经签到过了！',
                                       mention_ids=[from_contact.get_id()])
        elif text == '钱包':
            if from_contact.get_id() not in wallets.keys():
                await conversation.say(f'你还没有签到过！',
                                       [from_contact.get_id()])
            else:
                await conversation.say(
                    f'\n当前🍊：{wallets[from_contact.get_id()]["coin"]}🍊'
                    f'\n亲密度：{wallets[from_contact.get_id()]["relation"]}',
                    [from_contact.get_id()])
        elif text in zodiacs:
            url = f'https://api.salmoncross.xyz/v1/astroid'
            r = request('GET', url,
                        params={
                            "token": TOKEN,
                            "title": text,
                        })
            body = r.json()['data']
            today = json.loads(body['today'])
            await conversation.say(
                f'\n{text}运势：'
                f'\n速配星座{today["star"]}'
                f'\n幸运颜色：{today["color"]}'
                f'\n幸运数字：{today["number"]}'
                f'\n综合运势：{"🍊" * int(today["summary"])}'
                f'\n财运运势：{"🍊" * int(today["money"])}'
                f'\n工作运势：{"🍊" * int(today["career"])}'
                f'\n爱情运势：{"🍊" * int(today["love"])}'
                f'\n健康运势：{"🍊" * int(today["health"])}\n'
                f'\n综合运势：{today["presummary"]}'
                f'\n查看本周运势请输入$(星座)本周',
                [from_contact.get_id()]
            )
        elif text[:3] in zodiacs and text[3:] == '本周':
            url = f'https://api.salmoncross.xyz/v1/astroid'
            r = request('GET', url,
                        params={
                            "token": TOKEN,
                            "title": text[:3],
                        })
            body = r.json()['data']
            week = json.loads(body['week'])
            await conversation.say(
                f'\n{text}运势：'
                f'\n爱情运势: {week["love"]}\n'
                f'\n工作运势: {week["career"]}\n'
                f'\n财运运势: {week["money"]}\n'
                f'\n健康运势: {week["health"]}\n',
                [from_contact.get_id()]
            )
        elif text[:4] == '直播提醒':
            line = text.split(' ')
            if len(line) != 2:
                await conversation.say(
                    f'\n请输入正确的格式！'
                    f'\n直播提醒 [B站用户ID]',
                    [from_contact.get_id()]
                )
                return
            _, uid = line
            for stream in streams:
                if stream[0] == uid:
                    await conversation.say(
                        f'已经添加了主播{uid}的直播提醒！',
                        [from_contact.get_id()]
                    )
                    return
            url = "http://api.live.bilibili.com/room/" \
                  "v1/Room/get_status_info_by_uids?uids[]=" + uid
            r = request('GET', url)
            data = r.json()['data']
            if len(data) == 0:
                await conversation.say(
                    f'\n未找到直播间！'
                    f'\n请输入正确的B站用户ID！'
                    f'\n直播提醒 [B站用户ID]',
                    [from_contact.get_id()]
                )
                return
            streams.append([uid, room.room_id, False])
            with open('streams.json', 'w', encoding='utf-8') as f:
                json.dump(streams, f, ensure_ascii=False, indent=4)
            await conversation.say(
                f'成功添加了主播{data[uid]["uname"]}的直播提醒！',
                [from_contact.get_id()]
            )
        elif text[:6] == '取消直播提醒':
            line = text.split(' ')
            if len(line) != 2:
                await conversation.say(
                    f'\n请输入正确的格式！'
                    f'\n取消直播提醒 [B站用户ID]',
                    [from_contact.get_id()]
                )
                return
            _, uid = line
            for stream in streams:
                if stream[0] == uid:
                    streams.remove(stream)
                    with open('streams.json', 'w', encoding='utf-8') as f:
                        json.dump(streams, f, ensure_ascii=False, indent=4)
                    await conversation.say(
                        f'成功取消了用户{uid}的直播提醒！',
                        [from_contact.get_id()]
                    )
                    return
            await conversation.say(
                f'还没有添加过用户{uid}的直播提醒！',
                [from_contact.get_id()]
            )
        elif text == '前前中后':
            await conversation.say('！前前中后')


os.environ['TOKEN'] = os.getenv("UUID_TOKEN")
os.environ['WECHATY_PUPPET_SERVICE_ENDPOINT'] = "127.0.0.1:9001"
bot = OrangeBot()
asyncio.run(bot.start())
