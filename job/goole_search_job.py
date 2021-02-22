import requests
import pandas as pd
from bs4 import BeautifulSoup
import numpy as np
import pymongo
import time

"""
這個job本來是給老爸報名板橋社區大學公告課程用的，如果 google 有搜到就發 Line Msg 給我
未來可以考慮當做搜索jobs 使用
沒有經過特別測試，可能會跑失敗，需要加上失敗 error 上報
"""

def execute(coll, dict, _callbackLineMsg):
    targetStr = dict['name']

    # 只查30笔
    for i in range(0, 30, 10):
        print(i)
        page = '&start=' + str(i)
        url_bz = 'https://www.google.com/search?q=' + targetStr + page
        r = requests.get(url_bz)
        print('请求结果:' + str(r.status_code) + ', url=' + url_bz)
        soup = BeautifulSoup(r.content, "html.parser")

        # 找h3
        pid = soup.findAll('h3')

        for i in pid:
            print(i.text)
            if (targetStr == i.text):
                _callbackLineMsg("找到目标 -->" + targetStr)
                updateJobStatus(coll, dict)
                print('google job 结束')
                return
        time.sleep(3)
    print('google job 结束')

def updateJobStatus(coll, dict):
    myquery = {"_id": dict['_id']}
    newvalues = {"$set": {"status": "1"}}
    coll.update_one(myquery, newvalues)


