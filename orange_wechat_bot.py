import json
import os
import asyncio
import random
from dotenv import load_dotenv
from datetime import date, timedelta
from typing import List, Optional, Union
from requests import request
from wechaty_puppet import FileBox  # type: ignore
from wechaty import Wechaty, Contact
from wechaty.user import Message, Room

load_dotenv()
wallets = {
    "example_user": {
        "coin": 0,
        "relation": 0,
        "上次签到": str(date.today()),
    },
} if not os.path.exists("wallet.json") \
    else json.load(open("wallet.json"))
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


class OrangeBot(Wechaty):

    async def on_message(self, msg: Message):
        """
        listen for message event
        """
        from_contact: Optional[Contact] = msg.talker()
        name = from_contact.name
        text = msg.text()
        room: Optional[Room] = msg.room()
        if text in DRAW_LOTS.keys():
            conversation: Union[
                Room, Contact] = from_contact if room is None else room
            await conversation.ready()
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
            conversation: Union[
                Room, Contact] = from_contact if room is None else room
            await conversation.ready()
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
                                       [from_contact.get_id()])
        elif text == '钱包':
            conversation: Union[
                Room, Contact] = from_contact if room is None else room
            await conversation.ready()
            if from_contact.get_id() not in wallets.keys():
                await conversation.say(f'你还没有签到过！',
                                       [from_contact.get_id()])
            else:
                await conversation.say(
                    f'\n当前🍊：{wallets[from_contact.get_id()]["coin"]}🍊'
                    f'\n亲密度：{wallets[from_contact.get_id()]["relation"]}',
                    [from_contact.get_id()])


os.environ['TOKEN'] = os.getenv("UUID_TOKEN")
os.environ['WECHATY_PUPPET_SERVICE_ENDPOINT'] = "127.0.0.1:9001"
asyncio.run(OrangeBot().start())
