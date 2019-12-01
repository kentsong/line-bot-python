import abc

# 对应 java interface 实现
from oop.AbstractClass import Cat


class IFly(abc.ABC):  # {1}
    @abc.abstractmethod  # {2}
    def flyTo(self, place):
        pass


class FlyingCat(Cat, IFly):  # {3}
    def flyTo(self, place):
        return self.shout() + " I'm going to fly to " + place + ".";


def main():
    cat = FlyingCat("May")
    print(cat.flyTo("Taiwan"))


if __name__ == "__main__":
    main()
