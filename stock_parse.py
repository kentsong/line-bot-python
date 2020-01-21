#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov  1 18:59:05 2019

@author: kentsong
"""

import requests
import pandas as pd
from bs4 import BeautifulSoup
import numpy as np
import pymongo
import storage
import time


# 獲取 https://goodinfo.tw 網站信息，歷年股利、績效
def parseTwGoodsInfo(code, stockName):
    url_bz = 'https://goodinfo.tw/StockInfo/StockBzPerformance.asp'
    url_bonus = 'https://goodinfo.tw/StockInfo/StockDividendPolicy.asp'

    headers = {
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36',
        'referer': 'https://goodinfo.tw/StockInfo/StockBzPerformance.asp?STOCK_ID=2892'
    }

    form_data_bz = {
        'STOCK_ID': code,
        'YEAR_PERIOD': '9999',
        'RPT_CAT': 'M%5FYEAR',
        'STEP': 'DATA',
        'SHEET': 'PER%2FPBR'
    }

    form_data_dp = {
        'STOCK_ID': code,
        'YEAR_PERIOD': '9999'
    }

    r = requests.post(url_bz, data=form_data_bz, headers=headers)
    print('请求结果:' + str(r.status_code) + ', url=' + url_bz)
    soup = BeautifulSoup(r.content, "html.parser")

    #    print(soup)

    table = soup.find_all('table')[2]
    df = pd.read_html(str(table))

    # 基本数据表
    bzData = df[0]

    d1 = bzData[['年度', '股本(億)', 'EPS(元)', 'BPS(元)']].head(6)

    # 修改栏位名称
    d1.columns = ['年度', '股本(億)', 'EPS', '成長', 'BPS']
    # 提取目标栏位内容
    d2 = d1[['年度', 'EPS', 'BPS']]
    # 筛选不含'Q'的年度
    bool = ~d2.年度.str.contains('Q')
    d3 = d2[bool]
    bzResult = d3

    #############      股利脚本             ############
    r = requests.post(url_bonus, data=form_data_dp, headers=headers)
    print('请求结果:' + str(r.status_code) + ', url=' + url_bonus)
    soup = BeautifulSoup(r.content, "html.parser")
    table = soup.find_all('table', class_='solid_1_padding_4_0_tbl')[2]
    df = pd.read_html(str(table))
    # 股利数据
    bonusData = df[0]  # 获取list第0笔数据

    bonusData.columns = ['年度', '现金股利', '现金公积', '现金股利合计', '股票股利',
                         '股票公积', '股票股利合计', '股利合计', '現金(億)', '股票(千張)',
                         '現金(億)', '股票(千張', '股價年度', '最高', '最低',
                         '年均', '現金', '股票', '合計', '股利所屬期間',
                         'EPS(元)', '配息', '配股','合计']

    bonusData2 = bonusData[['年度', '现金股利合计', '股票股利合计', '股利合计', '最高', '最低', '年均']]
    bonusData2 = bonusData2.head(6)
    bonusResult = bonusData2

    ##合并报表
    result = pd.merge(bonusResult, bzResult, on='年度', how='outer')
    result['code'] = code
    result['name'] = stockName
    name_col = result.pop(result.columns[-1])
    code_col = result.pop(result.columns[-1])
    result.insert(0, 'code', code_col)
    result.insert(1, 'name', name_col)
    print('----合并报表结果----')
    print(result)

    return result


def parseStockHistorty(code):
    # 先檢查數據是否存在
    bol = storage.isStockHistortyExists(code)
    print('code =' + code + ', 是否存在数据=' + str(bol))

    if bol:
        print('mongodb 數據已存在')
        return False
    else:
        print('mongodb 數據不存在，開始處理...')

    # 查询股票代号是否存在
    url_twse = 'https://mis.twse.com.tw/stock/api/getStock.jsp?ch=' + code + '.tw'
    r = requests.get(url_twse)
    if r.status_code != 200:
        print('代號' + code + '查詢失敗')
    else:
        jsonObj = r.json()
        stockName = jsonObj['msgArray'][0]['n']
        print(stockName)

        # 檢查代號基本信息
    #    stock = twstock.realtime.get(code)
    #    if stock['success'] == False:
    #        print('代號'+code+'查詢失敗')
    #        return False
    #    else:
    #        stockName = stock['info']['name']
    #        print(stockName)

    result = parseTwGoodsInfo(code, stockName)

    # 连线Mongodb
    client = storage.getClient()
    # 选择db
    db = client.stockTW
    # 切换至对应 collection
    coll = db['stocks_history']
    # 查询 stocks_history 有没有对应的 code
    # coll.find({'code':'2892'}).count()
    # 走访数据
    #    for doc in coll.find({}):
    #        print(doc)

    # 插入数据
    # db["user"].insert_one({"name":"zhao"})

    # 衔接上面代码，用于插入数据库，遍历插入的，不知道有没有简单的办法啊~
    for i in range(len(result)):
        s = result.loc[i]
        # 这里加了str（）函数是无奈之举，DataFrame中的专有float64等数字格式使MongoDB无法识别，写入会报错，暂时先全部转换为字符串格式写入吧
        dic = {index: str(s[index]) for index in s.index}
        coll.insert_one(dic)
    #        print(dic)

    return 'ok'


def parseCurrentYearPrice(code):
    # 查询股票代号是否存在
    url_twse = 'https://mis.twse.com.tw/stock/api/getStock.jsp?ch=' + code + '.tw'
    r = requests.get(url_twse)
    if r.status_code != 200:
        print('代號' + code + '查詢失敗')
    else:
        jsonObj = r.json()
        stockName = jsonObj['msgArray'][0]['n']
        print(stockName)

    result = parseTwGoodsInfo(code, stockName)

    # 取表單第一筆記錄，並篩選欄位
    curDf = result.loc[0, ['年度', '最高', '最低', '年均']]
    msg = stockName + '(' + code + ')'', 年度：' + curDf[0] + ', 最高：' + str(curDf[1]) + ', 最低：' + str(
        curDf[2]) + ', 年均：' + str(curDf[3])
    return msg


def parseStockqOrgUrl(url):
    r = requests.get(url)

    if r.status_code != 200:
        print('查詢失敗')
        return '查詢失敗'

    soup = BeautifulSoup(r.content, "html.parser")
    table = soup.find_all('table', class_='indexpagetable')[3]
    df = pd.read_html(str(table))
    type(df)
    MA_df = df[0]
    # 取当前指数与(MA30+MA72)/2 的值
    MA = MA_df.iloc[1, 6]

    table = soup.find_all('table', class_='indexpagetable')[0]
    df = pd.read_html(str(table))
    type(df)
    index_df = df[0]
    type(index_df)
    index = index_df.iloc[1, 0]

    title = soup.title.string

    return title + ", 目前指数：" + index + ", (MA30+MA72)/2：" + MA


def parseStockqOrg():
    urlList = ['http://www.stockq.org/index/SHCOMP.php',
               'http://www.stockq.org/index/SHSZ300.php',
               'http://www.stockq.org/index/TWSE.php',
               'http://www.stockq.org/index/INDU.php']
    msg = ''

    for url in urlList:
        msg += parseStockqOrgUrl(url) + '\n'

    return msg


def parseEPSNear4Seasons(code):
    epsUrl = 'https://goodinfo.tw/StockInfo/StockBzPerformance.asp?STOCK_ID=' + code + '&YEAR_PERIOD=9999&RPT_CAT=QUAR'

    headers = {
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36',
        'referer': 'https://goodinfo.tw/StockInfo/StockBzPerformance.asp?STOCK_ID=2892'
    }

    r = requests.post(epsUrl, headers=headers)
    print('请求结果:' + str(r.status_code) + ', url=' + epsUrl)
    soup = BeautifulSoup(r.content, "html.parser")

    table = soup.find_all('table', class_='solid_1_padding_4_0_tbl')[0]
    df = pd.read_html(str(table))

    # 仅筛选前8笔季度、税后EPS栏位
    epdDf = df[0].iloc[[0, 1, 2, 3, 4, 5, 6, 7, 8], [0, 20]]
    epdDf.columns = ['季度', 'EPS']
    # 去除未揭露的EPS季度
    epdDf = epdDf[epdDf.EPS != '-']
    # 只取4个季度
    epdDf = epdDf.head(4)
    # 内容转换数值类型
    epdDf = epdDf.apply(pd.to_numeric, errors='ignore')
    # 确认 dateFrame 转换后数据格式为float64
    epdDf.dtypes
    sumDf = epdDf.sum()
    eps4Session = sumDf[1]
    print('近四季EPS=' + str(eps4Session))

    return str(eps4Session)


def queryStock(code):
    # 查询股票代号是否存在
    url_twse = 'https://mis.twse.com.tw/stock/api/getStock.jsp?ch=' + code + '.tw'
    r = requests.get(url_twse)
    if r.status_code != 200:
        print('代號' + code + '查詢失敗')
        return False
    else:
        jsonObj = r.json()
        stockName = jsonObj['msgArray'][0]['n']
        print(stockName)
        return jsonObj



def getStockPriceDf(code, year_num=3, eps=0):
    print(f'excute getStockPriceDf, params: code={code}, year_num={year_num}, eps={eps}')

    stockJson = queryStock(code);
    if stockJson == False:
        return '代號' + code + '查詢失敗'

    name = stockJson['msgArray'][0]['n']
    yPrice = stockJson['msgArray'][0]['y']

    # 历史报表
    result = parseTwGoodsInfo(code, name)
    # 近四季EPS
    if eps == 0:
        eps4Session = parseEPSNear4Seasons(code)
        eps4Session = float(eps4Session)
    else:  # 手動填入預估EPS
        eps4Session = float(eps)

    # 修改写入近四季EPS
    result.loc[0, 'EPS'] = eps4Session
    d1 = result
    return d1



def analysisStockPrice(code, year_num=3, eps=0):
    print(f'excute analysisStockPrice, params: code={code}, year_num={year_num}, eps={eps}')

    stockJson = queryStock(code);
    if stockJson == False:
        return '代號' + code + '查詢失敗'

    name = stockJson['msgArray'][0]['n']
    yPrice = stockJson['msgArray'][0]['y']

    # 历史报表
    result = parseTwGoodsInfo(code, name)
    # 近四季EPS
    if eps == 0:
        eps4Session = parseEPSNear4Seasons(code)
        eps4Session = float(eps4Session)
    else:  # 手動填入預估EPS
        eps4Session = float(eps)

    # 修改写入近四季EPS
    result.loc[0, 'EPS'] = eps4Session
    d1 = result

    d1 = d1.iloc[[0, 1, 2, 3, 4, 5], [2, 5, 6, 7, 8, 9]]

    d1['殖利率最高'] = d1.apply(lambda x: float(x['股利合计']) / float(x['最低']), axis=1)  # axis 0为列，1为行
    d1['殖利率最低'] = d1.apply(lambda x: float(x['股利合计']) / float(x['最高']), axis=1)
    d1['殖利率平均'] = d1.apply(lambda x: float(x['股利合计']) / float(x['年均']), axis=1)
    d1['本益比最高'] = d1.apply(lambda x: float(x['最高']) / float(x['EPS']), axis=1)
    d1['本益比最低'] = d1.apply(lambda x: float(x['最低']) / float(x['EPS']), axis=1)
    d1['本益比平均'] = d1.apply(lambda x: float(x['年均']) / float(x['EPS']), axis=1)
    print(d1)
    d1 = d1.apply(pd.to_numeric, errors='ignore')

    d1.dtypes
    # 近3年
    d2 = d1[d1.index < year_num]
    # 求平均 axis 0为列，1为行
    d2_avg = d2.mean(axis=0)

    # 取得最近一年股利 todo：2020年可能要修改逻辑
    bonus = d1.loc[d1.index[0], '股利合计']
    bonus = float(bonus)

    print('---- 殖利率法 ----')
    bonusHighPrice = bonus / d2_avg['殖利率最低']
    bonusMiddlePrice = bonus / d2_avg['殖利率平均']
    bonusLowPrice = bonus / d2_avg['殖利率最高']
    print('---- 本益比法 ----')
    epsHighPrice = d2_avg['本益比最高'] * eps4Session
    epsMiddlePrice = d2_avg['本益比平均'] * eps4Session
    epsLowPrice = d2_avg['本益比最低'] * eps4Session

    # 小數點保留2位四捨五入
    bonusHighPrice = round(bonusHighPrice, 2)
    bonusMiddlePrice = round(bonusMiddlePrice, 2)
    bonusLowPrice = round(bonusLowPrice, 2)
    epsHighPrice = round(epsHighPrice, 2)
    epsMiddlePrice = round(epsMiddlePrice, 2)
    epsLowPrice = round(epsLowPrice, 2)

    yPrice = float(yPrice)
    if yPrice >= bonusHighPrice:
        bonusResult = '高於昂貴價'
    elif yPrice >= bonusMiddlePrice:
        bonusResult = '高於合理價'
    elif yPrice < bonusMiddlePrice:
        bonusResult = '低於合理價'
    elif yPrice < bonusLowPrice:
        bonusResult = '低於便宜價'
    else:
        bonusResult = 'error'

    if yPrice >= epsHighPrice:
        epsResult = '高於昂貴價'
    elif yPrice >= epsMiddlePrice:
        epsResult = '高於合理價'
    elif yPrice < epsMiddlePrice:
        epsResult = '低於合理價'
    elif yPrice < epsLowPrice:
        epsResult = '低於便宜價'
    else:
        epsResult = 'error'

    msg1 = f'{name} ({code}) 分析结果：\n昨收價：{yPrice}\n殖利率法：{bonusResult}\n本益比法：{epsResult}\n\n'
    mgs2 = f'殖利率法 => 昂貴價：{bonusHighPrice} 合理價：{bonusMiddlePrice} 便宜價：{bonusLowPrice}\n\n'
    mgs3 = f'本益比法 => 昂貴價：{epsHighPrice} 合理價：{epsMiddlePrice} 便宜價：{epsLowPrice}'
    msgResult = msg1 + mgs2 + mgs3
    print(msgResult)

    return msgResult
