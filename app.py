import requests
import re
import random
import configparser
from bs4 import BeautifulSoup
from flask import Flask, request, abort
from imgurpython import ImgurClient
import os

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *

app = Flask(__name__)

## 從 Heroku Config Vars 讀取數據
channelAccessToken = os.environ.get('Channel_Access_Token', '')
channelSecret = os.environ.get('Channel_Secret', '')
kentUserId = os.environ.get('Kent_User_Id', '')
line_bot_api = LineBotApi(channelAccessToken)
handler = WebhookHandler(channelSecret)


@app.route("/index", methods=['GET'])
def home():
    print(channelAccessToken)
    print(channelSecret)

    return 'helloworld! linebot'


@app.route("/sendMsg", methods=['GET'])
def home():
    # get request body as text
    body = request.get_data(as_text=True)
    print(body)
    print("kentUserId=" + kentUserId)
    # 推訊息
    line_bot_api.push_message(kentUserId,
                              TextSendMessage(text='Hello World!'))
    return 'ok'


@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)

    app.logger.info("Request body: " + body)
    print("Request body: " + body)
    print("Request signature: " + signature)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'ok'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    print("event.reply_token:", event.reply_token)
    print("event.message.text:", event.message.text)
    print("event type = " + str(type(event)))
    print(event)
    if event.message.text.lower() == "test":
        content = 'test666'
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=content))
    else:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=event.message.text.lower()))
        return 0


if __name__ == '__main__':
    app.run()
