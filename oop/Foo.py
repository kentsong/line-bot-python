
class Foo:
    """一个简单的类实例"""
    i = 12345
    # def __init__(self, aaa):
    # self.i = aaa
    #     return
    def __init__(self):
        return

    def __init__(self, aaa):
        self.i = aaa
        return


    def f(self):
        self.i = 333;
        return 'hello world'

if __name__ == "__main__":
    # execute only if run as a script
    print('main')
    foo = Foo(888)
    print(foo.i)
    print(foo.f())
    print(foo.i)

