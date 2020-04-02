
class Foo:
    """一个简单的类实例"""
    i = 12345
    # def __init__(self, aaa):
    #     self.i = aaa
    #     return
    def __init__(self, aaa=None):
        self.i = aaa
        return

    def f(self):
        self.i = 333;
        return 'hello world'

if __name__ == "__main__":
    # execute only if run as a script
    print('main')
    foo1 = Foo()
    foo2 = Foo(888)
    print("foo1 i="+str(foo1.i))
    print("foo2 i="+str(foo2.i))
    foo2.f()
    print("foo2 after f, i="+str(foo2.i))
    print(vars(foo2))


