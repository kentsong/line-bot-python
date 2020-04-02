import abc
#abstract 抽象父类
class Animal(abc.ABC): #{1}
    def __init__(self,name="No-Name"):
        self._name = name
        self._shout_num = 3

    @property
    def shout_num(self):
        return self._shout_num
    @shout_num.setter  ##这不知道是干嘛的
    def shout_num(self,num):
        self._shout_num = num

    def shout(self):
        result = ""
        for _ in range(self._shout_num):
            result += self._getShoutSound()+" "
        return "My name is "+self._name+". "+result
    @abc.abstractmethod  #{2}
    def _getShoutSound(self):
        pass

class Cat(Animal):
    def _getShoutSound(self): #{3}
        return "meow~"
    def move(self):
        print(self._name + " move..")

class Dog(Animal):
    def _getShoutSound(self):
        return "woof~"


cat = Cat("ada")
print(cat.shout())
cat.move()
print(cat.shout_num)

dog = Dog("旺旺队ˋ")
print(dog.shout())