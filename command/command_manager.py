import exchange_rate
import stockorg
import twse
import goodsinfo
import collections
import util.error_util as error_util
import os

"""
管理 command input/output 流程框架 
"""

myDict = collections.OrderedDict()


def add_command(cls):
    myDict[str(cls.description())] = cls


# 在此添加功能
add_command(exchange_rate.ExchangeRate())  # 外幣匯率
add_command(exchange_rate.ExchangeRateChart())  # 外幣走勢
add_command(stockorg.StockOrgIndex())  # stockorg指数
add_command(twse.TwPrice())
add_command(goodsinfo.BaseAnalysisPrice())
add_command(goodsinfo.MyWatchStock())

def handle_command(command):
    # 空白格區分入參
    params = command.split(" ")

    # 所有功能介绍
    if params[0] == "所有功能":
        return list_dict_prefix()

    if myDict.__contains__(params[0]) == False:
        # return "目前無此功能，輸入：所有功能，查看現有功能。"
        return False
    else:
        cmdCls = myDict[params[0]]
        # 功能说明
        if len(params) == 2 and params[1] == 'help':
            return cmdCls.description_how_to_use()
        # 功能执行
        try:
            print(f'process command "{params[0]}"')
            return cmdCls.process(params)
        except Exception as err:
            return error_util.printTrace(err)


def list_dict_prefix():
    str = "目前支援功能：" + os.linesep
    for i, key in enumerate(myDict.keys(), start=1):
        str += (f'{i}.{key}' + os.linesep)
    return str


if __name__ == '__main__':
    # print(str(myDict))
    # print(myDict.__contains__('外幣'))
    # print(myDict.__contains__('外幣2'))

    # print(handle_command("外幣 CNY"))
    # docker run --name nginx-container -p 7777:80 -d mynginx
    print(list_dict_prefix())
    # print(handle_command("外幣 help"))
