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


def parseStockHistorty(code):
    
    #先檢查數據是否存在
    bol = storage.isStockHistortyExists(code)
    print('code ='+code +', 是否存在数据='+str(bol))
    
    if bol:
        print('mongodb 數據已存在')
        return False
    else:
        print('mongodb 數據不存在，開始處理...')
    
    #查询股票代号是否存在
    url_twse = 'https://mis.twse.com.tw/stock/api/getStock.jsp?ch='+code+'.tw'
    r = requests.get(url_twse)
    if r.status_code != 200:
        print('代號'+code+'查詢失敗')
    else:
        jsonObj = r.json()
        stockName = jsonObj['msgArray'][0]['n']
        print(stockName)    


    
    #檢查代號基本信息
#    stock = twstock.realtime.get(code)
#    if stock['success'] == False:
#        print('代號'+code+'查詢失敗')
#        return False
#    else:
#        stockName = stock['info']['name']
#        print(stockName)
    
    url_bz = 'https://goodinfo.tw/StockInfo/StockBzPerformance.asp'
    url_bonus = 'https://goodinfo.tw/StockInfo/StockDividendPolicy.asp'
    
    headers = {
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36',
        'referer':'https://goodinfo.tw/StockInfo/StockBzPerformance.asp?STOCK_ID=2892'
    }

    form_data = {
        'STOCK_ID': code,
        'YEAR_PERIOD': '9999',
        'RPT_CAT': 'M%5FYEAR',
        'STEP': 'DATA',
        'SHEET': 'PER%2FPBR'
    }
    
    
    r = requests.post(url_bz, data=form_data, headers=headers)
    print('请求结果:'+str(r.status_code)+', url='+url_bz)
    soup = BeautifulSoup(r.content, "html.parser")
    
#    print(soup)
    
    table = soup.find_all('table')[2]
    df = pd.read_html(str(table))
    
    #基本数据表
    bzData = df[0]
    
    d1 = bzData[['年度','股本(億)','EPS(元)','BPS(元)']].head(6)
    
    #修改栏位名称
    d1.columns = ['年度', '股本(億)', 'EPS', '成長', 'BPS']
    #提取目标栏位内容
    d2 = d1[['年度', 'EPS', 'BPS']]
    #筛选不含'Q'的年度
    bool = ~d2.年度.str.contains('Q')
    d3 = d2[bool]
    bzResult = d3
    
    
    
    
    
    #############      股利脚本             ############
    r = requests.post(url_bonus, data=form_data, headers=headers)
    print('请求结果:'+str(r.status_code)+', url='+url_bonus)
    soup = BeautifulSoup(r.content, "html.parser")
    table = soup.find_all('table')[5]
    df = pd.read_html(str(table))
    #股利数据
    bonusData = df[11] #获取list第11笔数据
    
    bonusData.columns = ['年度','现金股利','现金公积','现金股利合计','股票股利','股票公积','股票股利合计','股利合计','現金(億)','股票(千張)','合計(百萬)','佔淨利',
                         '現金(億)','股票(千張','股價年度','最高','最低', '年均','現金','股票','合計','股利所屬期間','EPS(元)','配息','配股','合计']
    
    bonusData2 = bonusData[['年度', '现金股利合计','股票股利合计','股利合计','最高','最低','年均']]
    
    bonusData2 = bonusData2.head(6)
#    print(bonusData2)
    bonusResult = bonusData2
    
    
    ##合并报表
    result = pd.merge(bonusResult, bzResult, on='年度',how='outer')
    result['code'] = code
    result['name'] = stockName
    name_col = result.pop(result.columns[-1])
    code_col = result.pop(result.columns[-1])
    result.insert(0, 'code', code_col)
    result.insert(1, 'name', name_col)
    print('----合并报表结果----')
    print(result)

    
    
    
    
    
    #连线Mongodb
    client = storage.getClient()
    #选择db
    db = client.stockTW
    #切换至对应 collection
    coll = db['stocks_history']
    #查询 stocks_history 有没有对应的 code
    #coll.find({'code':'2892'}).count()
    #走访数据 
#    for doc in coll.find({}):
#        print(doc)
    
    #插入数据
    #db["user"].insert_one({"name":"zhao"})
    
    
    
    #衔接上面代码，用于插入数据库，遍历插入的，不知道有没有简单的办法啊~
    for i in range(len(result)):
        s = result.loc[i]
    #这里加了str（）函数是无奈之举，DataFrame中的专有float64等数字格式使MongoDB无法识别，写入会报错，暂时先全部转换为字符串格式写入吧
        dic = {index:str(s[index]) for index in s.index}
        coll.insert_one(dic)
#        print(dic)
        
        
    
    return 'ok'