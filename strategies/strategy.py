from nseapi import NseApi


class Strategy:

    def __init__(self):
        self.nse_api = NseApi()
        self.name = __name__

    def run(self):
        pass

    def back_test(self):
        pass
