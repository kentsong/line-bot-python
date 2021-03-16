import command_base
import stock_parse

'''
StockOrg 指数查询
'''
class StockOrgIndex(command_base.BaseCommand):
    def __init__(self):
        self.prefix = "stockorg"
        self.how_to_use = f''

        # 调用父类的构函
        command_base.BaseCommand.__init__(self, self.prefix, self.how_to_use)

    def check_param(self, param_array):
        return True

    # 覆写父类的方法
    def process(self, params):
        return stock_parse.parseStockqOrg()
