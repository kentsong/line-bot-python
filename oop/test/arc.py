"""
命令抽象类
"""


class MsgCommand(object):

    def __init__(self, desc, desc_use):
        self._description = desc
        self._desc_how_to_use = desc_use

    def description(self):
        return self._description

    def description_how_to_use(self):
        return self._desc_how_to_use

    def check_param(self, command):
        return True

    def process(self, command):
        raise Exception('handle_command not implemented.')


class exchange_rate(MsgCommand):

    def __init__(self):
        # 调用父类的构函
        MsgCommand.__init__(self, "汇率查询", "汇率查询使用说明")

    # 覆写父类的方法
    def process(self, command):
        return "处理了 exchange_rate"


if __name__ == '__main__':
    command = exchange_rate()
    params = '1-2-3'
    print(command.description())
    print(command.description_how_to_use())
    print(command.process(params))

    import collections
    d = collections.OrderedDict()
    d[command.description()] = command
    # d['1'] = '1'
    print(d)
    for key, value in d.items():
        print("key="+key+", value="+str(value))
