import requests
import re
import random
import configparser
from bs4 import BeautifulSoup
from flask import Flask, request, abort
from imgurpython import ImgurClient
import os
# from flask_apscheduler import APScheduler  # 引入APScheduler

import time

# 本地py引入
import storage
import stock_parse

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *


class Config(object):
    JOBS = [
        # {
        #     'id': 'job1',
        #     'func': 'app:test_data',
        #     'args': '',
        #     'trigger': {
        #         'type': 'cron',
        #         'day_of_week': "mon-fri",
        #         'hour': '0-23',
        #         'minute': '0-59',
        #         'second': '*/30'
        #     }
        #
        # },
        {
            'id': 'job_announce',
            'func': 'app:test_data',
            'args': '',
            'trigger': 'interval',
            'seconds': 5
        }
    ]
    SCHEDULER_API_ENABLED = True

app = Flask(__name__)

## 從 Heroku Config Vars 讀取數據
channelAccessToken = os.environ.get('Channel_Access_Token', '')
channelSecret = os.environ.get('Channel_Secret', '')
kentUserId = os.environ.get('Kent_User_Id', '')
line_bot_api = LineBotApi(channelAccessToken)
handler = WebhookHandler(channelSecret)


def test_data():
    print("I am working:%s"+time.asctime())

@app.route("/home", methods=['GET'])
def home():
    print(channelAccessToken)
    print(channelSecret)

    return 'helloworld! linebot'


@app.route("/sendMsg", methods=['GET'])
def sendMsg():
    # get request body as text
    body = request.get_data(as_text=True)
    print(body)
    print("kentUserId=" + kentUserId)
    # 推訊息
    line_bot_api.push_message(kentUserId,
                              TextSendMessage(text='Hello World!'))
    return 'ok'


@app.route("/controller", methods=['GET'])
def receiceCommend():
    # args取get方式参数
    ctype = request.args.get('type')
    code = request.args.get('code')

    resultMsg = 'request ctype=' + ctype + ', code=' + code
    print(resultMsg)
    if ctype == 'parseHistory':
        msg = stock_parse.parseStockHistorty(code)
        return resultMsg + ", 处理结果=" + msg
    return 'type not mapping...'


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

    reqMsg = event.message.text.lower()
    if reqMsg == "test":
        content = 'test666'
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=content))
    elif reqMsg.find("殖利率法") != -1:
        x = reqMsg.split(" ")
        code = x[1]
        print(code)
        stock_parse.parseStockHistorty(code)
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=code))
    elif reqMsg.find("年度股價") != -1:
        x = reqMsg.split(" ")
        code = x[1]
        print(code)
        msg = stock_parse.parseCurrentYearPrice(code)
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=msg))
    elif reqMsg.find("stockorg") != -1:
        msg = stock_parse.parseStockqOrg()
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=msg))    
    else:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=event.message.text.lower()))
        return 0


def job1():
    print ("%s: 执行任务1"  % time.asctime())

def job2():
    print ("%s: 执行任务2"  % time.asctime())




if __name__ == '__main__':
    # scheduler = APScheduler();
    # app.config.from_object(Config())
    # scheduler.init_app(app)
    # scheduler.start()
    app.run()
