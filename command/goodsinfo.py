import command_base
import stock_parse
import os

'''
基本面分析
'''
class BaseAnalysisPrice(command_base.BaseCommand):
    def __init__(self):
        self.prefix = "基本面分析"
        self.how_to_use = f'簡易分析本益比、股利價格位階 {os.linesep}' \
                          f'輸入範例：基本面分析 2892 3{os.linesep}' \
                          f'參數1:股票代號 {os.linesep}' \
                          f'參數2:向前估算年份'\
                          f'參數3(選填):手動帶入近四季EPS'

        # 调用父类的构函
        command_base.BaseCommand.__init__(self, self.prefix, self.how_to_use)

    def check_param(self, param_array):
        return True

    # 覆写父类的方法
    def process(self, params):
        num = len(params)
        if num <= 2:
            code = params[1]
            msg = stock_parse.analysisStockPrice(code)
        elif num == 3:
            code = params[1]
            year = float(params[2])
            msg = stock_parse.analysisStockPrice(code, year)
        elif num == 4:
            code = params[1]
            year = float(params[2])
            eps = float(params[3])
            msg = stock_parse.analysisStockPrice(code, year, eps)
        else:
            msg = '參數有誤'
        return msg