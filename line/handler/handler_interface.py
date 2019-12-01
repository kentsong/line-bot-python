import abc
from line.handler.stockorg import StockOrg


# 对应 java interface 实现，运用多重继承

# line 信息事件处理器者
class IHandler(abc.ABC):
    # def __init__(self, name="No-Name"):
    #     self._name = name

    @abc.abstractmethod
    def handle(self, text):
        pass


class Handler(StockOrg, IHandler):
    def handle(self, text):
        print(self.hello())
        return "handle " + text

    def getShoutSound(self):
        return "meow~"


def main():
    s = Handler()
    print(s.handle('interface'))


if __name__ == "__main__":
    main()
