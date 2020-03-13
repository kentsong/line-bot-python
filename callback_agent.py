import re
import exrate
import stock_parse
import os


def handle_message(msg):
    if re.match('外幣[A-Z]{3}', msg):
        currency = msg[2:5]  # 外幣代號
        currency_name = exrate.getCurrencyName(currency)
        if currency_name == "無可支援的外幣":
            return "無可支援的外幣." + os.linesep + " 以下是支援幣種:" + os.linesep + str(exrate.currency_list)
        else:
            return exrate.showCurrency(currency)
        return 0
    if re.match('外幣走勢圖[A-Z]{3}', msg):
        currency = msg[5:8]  # 外幣代號
        currency_name = exrate.getCurrencyName(currency)
        if currency_name == "無可支援的外幣":
            return "無可支援的外幣."
        else:
            return exrate.showHistory(currency)
        return 0
    elif re.match('test', msg):
        content = 'test666'
        return content
    elif msg.find("年度股價") != -1:
        x = msg.split(" ")
        code = x[1]
        print(code)
        return stock_parse.parseCurrentYearPrice(code)
    elif msg.find("stockorg") != -1:
        try:
            msg = stock_parse.parseStockqOrg()
        except:
            msg = "stockorg 處理異常"
        return msg
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
        return msg
    else:
        return msg
