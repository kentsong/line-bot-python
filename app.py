import sys
# 配置本地環境，對照 Folder
sys.path.append('command')
from flask import Flask, request, abort, send_file
import os
import local_env_loader #本地環境變數
import io
import pandas as pd
import re
import exrate
import job_manager
import command.command_manager as cmdManager
# from flask_apscheduler import APScheduler  # 引入APScheduler
import time

# 本地py引入
import storage
import stock_parse
import support.smtp_helper as smtp_helper

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


@app.route("/", methods=['GET'])
def home():
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

@app.route("/jobs", methods=['GET'])
def jobs():
    msg = 'ok'
    try:
        job_manager.start(callbackLineMsg)
    except:
        msg = "error"
    return msg


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

# 测试 url http://127.0.0.1:5000/callbackTest?msg=stockorg
# msg 填入测试 command
@app.route("/callbackTest", methods=['GET'])
def callbackTest():
    msg = request.args.get('msg')
    return cmdManager.handle_command(msg)

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    print("event.reply_token:", event.reply_token)
    print("event.message.text:", event.message.text)
    print("event type = " + str(type(event)))
    print(event)
    profile = line_bot_api.get_profile(event.source.user_id)
    user_name = profile.display_name  # 使用者名稱
    uid = profile.user_id  # 發訊者ID

    reqMsg = event.message.text.lower()
    # command框架處理
    result = cmdManager.handle_command(reqMsg)
    if not result:
        handle_message_internal(uid, reqMsg)
    else:
        line_bot_api.push_message(uid, TextSendMessage(result))
    return 0

def handle_message_internal(uid, msg):
    if re.match('外幣[A-Za-z]{3}', msg):
        currency = msg[2:5]  # 外幣代號
        currency_name = exrate.getCurrencyName(currency)
        if currency_name == "無可支援的外幣":
            resultMsg = "無可支援的外幣." + os.linesep + " 以下是支援幣種:" + os.linesep + str(exrate.currency_list)
            line_bot_api.push_message(uid, TextSendMessage(resultMsg))
        else:
            resultMsg = exrate.showCurrency(currency.upper())
            line_bot_api.push_message(uid, TextSendMessage(resultMsg))
    elif re.match('外幣走勢圖[A-za-z]{3}', msg):
        currency = msg[5:8]  # 外幣代號
        currency_name = exrate.getCurrencyName(currency)
        if currency_name == "無可支援的外幣":
            resultMsg = "無可支援的外幣."
            line_bot_api.push_message(uid, TextSendMessage(resultMsg))
        else:
            resultMsg = exrate.showHistory(currency.upper())
            line_bot_api.push_message(uid, ImageSendMessage(original_content_url=resultMsg, preview_image_url=resultMsg))
    elif msg == "test":
        content = 'test666'
        line_bot_api.push_message(uid, TextSendMessage(content))
    elif msg.find("年度股價") != -1:
        x = msg.split(" ")
        code = x[1]
        print(code)
        resultMsg =  stock_parse.parseCurrentYearPrice(code)
        line_bot_api.push_message(uid, TextSendMessage(resultMsg))
    elif msg.find("stockorg") != -1:
        try:
            msg = stock_parse.parseStockqOrg()
        except:
            msg = "stockorg 處理異常"
        line_bot_api.push_message(uid, TextSendMessage(msg))
    elif msg.find("基本面分析") != -1:
        x = msg.split(" ")
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
        line_bot_api.push_message(uid, TextSendMessage(msg))
    elif msg.find("sendmail") != -1:
        line_bot_api.push_message(uid, smtp_helper.sendEmail())
    else:
        line_bot_api.push_message(uid, TextSendMessage(msg))

def callbackLineMsg(msg):
    print('callbackLineMsg --->'+msg)
    line_bot_api.push_message(kentUserId,
                              TextSendMessage(text=msg))


if __name__ == '__main__':
    app.run(debug=True)

