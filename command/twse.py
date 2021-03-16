import command_base
import stock_parse

'''
台股股價
'''
class TwPrice(command_base.BaseCommand):
    def __init__(self):
        self.prefix = "年度股價"
        self.how_to_use = f'輸入台股代號，例如：年度股價 2330'

        # 调用父类的构函
        command_base.BaseCommand.__init__(self, self.prefix, self.how_to_use)

    def check_param(self, param_array):
        return True

    # 覆写父类的方法
    def process(self, params):
        return stock_parse.parseCurrentYearPrice(params[1])