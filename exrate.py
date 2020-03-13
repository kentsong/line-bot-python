# 匯率服務
from imgurpython import ImgurClient
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from matplotlib.font_manager import FontProperties # 設定字體
chinese_font = matplotlib.font_manager.FontProperties(fname='msjh.ttf') # 引入同個資料夾下支援中文字檔
import twder
import os
from imgurpython import ImgurClient

######
# 本地跑 flask 要配置
# 1.建立檔案： ~/.matplotlib/matplotlibrc
# 2.加入文字：backend: TkAgg
#####

## heroku env variable
client_id = os.environ.get('IMGUR_CLIENT_ID', '')
client_secret = os.environ.get('IMGUR_CLIENT_SECRET', '')
album_id = os.environ.get('IMGUR_ALBUM_ID', '')
access_token = os.environ.get('IMGUR_ACCESS_TOKEN', '')
refresh_token = os.environ.get('IMGUR_REFRESH_TOKEN', '')


currency_list = {
    "USD": "美元",
    "JPY": "日圓",
    "HKD": "港幣",
    "GBP": "英鎊",
    "AUD": "澳幣",
    "CAD": "加拿大幣",
    "CHF": "瑞士法郎",
    "SGD": "新加坡幣",
    "ZAR": "南非幣",
    "SEK": "瑞典幣",
    "NZD": "紐元",
    "THB": "泰幣",
    "PHP": "菲國比索",
    "IDR": "印尼幣",
    "KRW": "韓元",
    "MYR": "馬來幣",
    "VND": "越南盾",
    "CNY": "人民幣",
}


def getCurrencyName(currency):
    try:
        currency_name = currency_list[currency.upper()]
    except:
        return "無可支援的外幣"
    return currency_name


# 查詢匯率
def showCurrency(msg):  # msg為外幣代碼
    content = ""
    currency_name = getCurrencyName(msg)
    if currency_name == "無可支援的外幣": return "無可支援的外幣"
    # 資料格式 {貨幣代碼: (時間, 現金買入, 現金賣出, 即期買入, 即期賣出), ...}
    currency = twder.now(msg)
    # 當下時間
    now_time = str(currency[0])
    # 銀行現金買入價格
    buying_cash = "無資料" if currency[1] == '-' else str(float(currency[1]))
    # 銀行現金賣出價格
    sold_cash = "無資料" if currency[2] == '-' else str(float(currency[2]))
    # 銀行即期買入價格
    buying_spot = "無資料" if currency[3] == '-' else str(float(currency[3]))
    # 銀行即期賣出價格
    sold_spot = "無資料" if currency[4] == '-' else str(float(currency[4]))

    try:
        middle_spot = str((float(buying_spot) + float(sold_spot)) / 2)
    except:
        middle_spot = ''

    content += currency_name + "最新掛牌時間為: " + now_time + '\n ---------- \n 現金買入價格: ' + buying_cash + '\n 現金賣出價格: ' + str(
        sold_cash) + '\n 即期買入價格: ' + buying_spot + '\n 即期賣出價格: ' + sold_spot + '\n \n 即期中間價: '+ middle_spot
    return content

def showHistory(msg):
    # step1.读取表单
    dfs = pd.read_html('https://rate.bot.com.tw/xrt/quote/l6m/'+msg)
    df2 = dfs[0]

    # step2.过滤
    # 方法一:删除含有na的栏位
    # df1.dropna(axis='columns', inplace=True)

    # 方法二: 选取第0~6列
    df2 = df2.iloc[:, 0:6]

    # step3. 重新命名 colnums
    df2.columns = ['date', '幣別', '現金買入', '現金賣出', '即期買入', '即期賣出']
    # 修改 index
    df2.set_index('date')

    df2 = df2.iloc[::-1]  # row 順序反轉，因原始資料是從最新開始排

    print(df2)

    # df2.plot(kind='line', figsize=(12, 6), x='date', y=[u'即期買入', u'即期賣出'])
    df2.plot(kind='line', figsize=(12, 6), x='date', y=['即期買入', '即期賣出'])
    plt.legend(prop=chinese_font)  # 支援中文字
    plt.title("即期匯率", fontsize=40, fontproperties=chinese_font)
    plt.savefig(msg+".png")
    plt.show()
    plt.close()



    ### 上传图片到 imgur
    client = ImgurClient(client_id, client_secret, access_token, refresh_token)
    config = {
        'album': 'g4yhAr4',
        'name': 'test-name!',
        'title': 'test-title',
        'description': 'test-description'
    }
    print("Uploading image... ")
    image = client.upload_from_path(msg+'.png', config=config, anon=False)
    print("Done")

    #### 上传完成图片信息
    type(image)
    return image['link']






