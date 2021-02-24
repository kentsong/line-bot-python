import sys
# sys.path.append('command')
# print("kentsong:"+str(sys.path))

import exchange_rate
import collections
import util.error_util as error_util


"""
管理 command input/output 流程框架 
"""

myDict = collections.OrderedDict()

def add_command(cls):
    myDict[str(cls.description())] = cls

# 在此添加功能
add_command(exchange_rate.exchange_rate()) # 外幣匯率

def handle_command(command):
    # 空白格區分入參
    params = command.split(" ")

    if params[0] == "所有功能":
        return "列出所有功能"

    if myDict.__contains__(params[0]) == False:
        return "目前無此功能，輸入：所有功能，查看現有功能。"
    else:
        cmdCls = myDict[params[0]]
        try:
            print(f'process command "{params[0]}"')
            return cmdCls.process(params)
        except Exception as err:
            return error_util.printTrace(err)


if __name__ == '__main__':
    # print(str(myDict))
    # print(myDict.__contains__('外幣'))
    # print(myDict.__contains__('外幣2'))

    print(handle_command("外幣 CNY"))
    #docker run --name nginx-container -p 7777:80 -d mynginx

