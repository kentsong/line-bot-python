#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov  1 18:33:48 2019

@author: kentsong
"""

import pymongo
import os

mongo_user = os.environ.get('Mongo_User', '')
mongo_pwd = os.environ.get('Mongo_Pwd', '')

client = pymongo.MongoClient("mongodb://"+mongo_user+":"+mongo_pwd+"@cluster0-shard-00-00-sefrw.gcp.mongodb.net:27017,cluster0-shard-00-01-sefrw.gcp.mongodb.net:27017,cluster0-shard-00-02-sefrw.gcp.mongodb.net:27017/test?ssl=true&replicaSet=Cluster0-shard-0&authSource=admin&retryWrites=true&w=majority")

def isStockHistortyExists(code):
    #连线Mongodb
    #选择db
    db = client.stockTW
    #切换至对应 collection
    coll = db['stocks_history']
    #查询 stocks_history 有没有对应的 code
    num = coll.find({'code':code}).count()
    return num != 0

def getClient():
    return client
