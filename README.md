# Orange Wechat Bot
An Wechat group chat bot for entertainment, etc.

## Features

* Auto reply to messages sent by users in the group.
* Track members who check-in daily to the group and reward in coins and relationship.
* Tarot, Zhuge, Zhouyi, and other fortune-telling methods.
* Remind users of their following Bilibili streamers status.
* Add your own features.

## Prerequisites
* [Python 3.7+](https://www.python.org/downloads/)
* [Salmon Cross API](https://www.salmoncross.xyz/)
* [Wechaty Gateway](https://wechaty.js.org/docs/v0/gateway/)
* [Wechaty](https://wechaty.js.org/docs/v0/wechaty/)
* [Pad Local](https://pad-local.com/)
* [Docker](https://www.docker.com/)

## Installation
* Get a Pad Local token from [Pad Local](https://pad-local.com/)
* Get a Salmon Cross token from [Salmon Cross](https://www.salmoncross.xyz/)
* Modify the environment variables and rename `bot.env.example` and `gateway.sh.example` to `bot.env` and `gateway.sh`. You can generate uuid by:
  ```python
  import uuid
  print(uuid.uuid4())
  ```
* Intall Docker:
    ```bash
    brew cask install docker
    ```

* Intall and Run Wechaty Gateway:
    ```bash
    chmod +x gateway.sh
    ./gateway.sh
    ```

* Create Python virtual environment:
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

* Intall Wechaty:
    ```bash
    pip install python-dotenv
    pip install wechaty
    ```
  
* Run Orange Wechat Bot:
    ```bash
    python3 orange_wechat_bot.py
    ```