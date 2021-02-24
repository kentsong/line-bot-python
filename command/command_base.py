"""
command 抽象類
"""
class BaseCommand(object):

    def __init__(self, desc, desc_use):
        self._description = desc
        self._desc_how_to_use = desc_use

    def description(self):
        return self._description

    def description_how_to_use(self):
        return self._desc_how_to_use

    def check_param(self, param_array):
        return True

    def process(self, param_array):
        raise Exception('handle_command not implemented.')