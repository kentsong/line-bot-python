import line.handler.handler_interface as handler
from line.handler.stockorg import StockOrg
from collections import ChainMap


class Foo(StockOrg, handler.IHandler):
    def handle(self, text):
        print(self.hello())
        return "handle " + text

    def getShoutSound(self):
        return "meow~"

class Foo2(StockOrg, handler.IHandler):
    def handle(self, text):
        print(self.hello())
        return "handle2 " + text

    def getShoutSound(self):
        return "meow~2"


def main():
    cat = Foo()
    cat2 = Foo()
    print(cat.hello())
    print(cat.handle('dog'))

    m1 = {'color': cat, 'user': cat2}
    m2 = {'name': cat, 'age': '1'}
    chainMap = ChainMap(m1, m2)
    print(chainMap.get('key'))
    print(chainMap)
    print(chainMap.get('name'))
    # chainMap.
    print(chainMap.get('age'))


if __name__ == "__main__":
    main()



# s = handler.Handler()
# print(s.handle('text'))


# s = stockorg.StockOrg("text")
# # print(s.handle('tttt'))