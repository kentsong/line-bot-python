import requests
import re
import random
import configparser
from bs4 import BeautifulSoup
from flask import Flask, request, abort, send_file
from imgurpython import ImgurClient
import os
import io
import pandas as pd
import xlsxwriter

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

app = Flask(__name__)

## 從 Heroku Config Vars 讀取數據
channelAccessToken = os.environ.get('Channel_Access_Token', '')
channelSecret = os.environ.get('Channel_Secret', '')
kentUserId = os.environ.get('Kent_User_Id', '')
line_bot_api = LineBotApi(channelAccessToken)
handler = WebhookHandler(channelSecret)


def test_data():
    print("I am working:%s" + time.asctime())


@app.route("/", methods=['GET'])
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
    try:
        msg = stock_parse.parseStockqOrg()
    except:
        msg = "stockorg 處理異常"
    line_bot_api.push_message(kentUserId,
                              TextSendMessage(text=msg))
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


@app.route("/downloadExcel", methods=['GET'])
def downloadExcel():
    # args取get方式参数
    code = request.args.get('code')
    year = request.args.get('year')
    eps = request.args.get('eps')

    df1 = stock_parse.getStockPriceDf(code, 3, 0)

    buf = io.BytesIO()
    excel_writer = pd.ExcelWriter(buf, engine="xlsxwriter")
    df1.to_excel(excel_writer, sheet_name="sheet1", index=False)
    excel_writer.save()
    excel_data = buf.getvalue()
    buf.seek(0)
    
    return send_file(buf,
                     mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                     attachment_filename="test11311.xlsx",
                     as_attachment=True,
                     cache_timeout=0)


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
        replyMsg(event, content)
    elif reqMsg.find("年度股價") != -1:
        x = reqMsg.split(" ")
        code = x[1]
        print(code)
        msg = stock_parse.parseCurrentYearPrice(code)
        replyMsg(event, msg)
    elif reqMsg.find("stockorg") != -1:
        try:
            msg = stock_parse.parseStockqOrg()
        except:
            msg = "stockorg 處理異常"
        replyMsg(event, msg)
    elif reqMsg.find("基本面分析") != -1:
        x = reqMsg.split(" ")
        num = len(x)
        if num <= 2:
            code = x[1]
            msg = stock_parse.analysisStockPrice(code)
        elif num == 3:
            code = x[1]
            year = float(x[2])
            msg = stock_parse.analysisStockPrice(code, year)
        elif num == 4:
            code = x[1]
            year = float(x[2])
            eps = float(x[3])
            msg = stock_parse.analysisStockPrice(code, year, eps)
        else:
            msg = '參數有誤'
        print(code)
        replyMsg(event, msg)
    else:
        replyMsg(event, event.message.text.lower())
        return 0

def replyMsg(event, msg):
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=msg))


if __name__ == '__main__':
    app.run()
