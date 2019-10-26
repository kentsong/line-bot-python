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
channelAccessToken = os.environ.get('Channel_Access_Token', '')
channelSecret = os.environ.get('Channel_Secret', '')
line_bot_api = LineBotApi(channelAccessToken)
handler = WebhookHandler(channelSecret)


@app.route("/index", methods=['GET'])
def home():
    print(channelAccessToken)
    print(channelSecret)

    return 'helloworld!'


@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    # print("body:",body)
    app.logger.info("Request body: " + body)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'ok'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    print("event.reply_token:", event.reply_token)
    print("event.message.text:", event.message.text)
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
