import command_base
import exrate
import re
import os

class exchange_rate(command_base.BaseCommand):
    def __init__(self):
        self.prefix = "外幣"
        self.how_to_use = f'輸入範例：外幣CNY' \
                          f'{os.linesep}' \
                          f'目前支援幣種：{os.linesep}' \
                          f'{str(exrate.currency_list)}'

        # 调用父类的构函
        command_base.BaseCommand.__init__(self, self.prefix, self.how_to_use)

    def check_param(self, param_array):
        return re.match('[A-Za-z]{3}', param_array[0])

    # 覆写父类的方法
    def process(self, params):
        if self.check_param(params) == False:
            return "參數有誤"

        currency = params[1]  # 末三位是外幣代號
        currency_name = exrate.getCurrencyName(currency)
        if currency_name == "無可支援的外幣":
            resultMsg = "無可支援的外幣." + os.linesep + " 以下是支援幣種:" + os.linesep + str(exrate.currency_list)
        else:
            resultMsg = exrate.showCurrency(currency.upper())
        return resultMsg

# Testing
if __name__ == '__main__':
    command1 = exchange_rate()
    print(command1.description())
    print(command1.description_how_to_use())
    print('-------------------------------')
    # msg = command1.process("外幣CNY")
    # print(msg)
