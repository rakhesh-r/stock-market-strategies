from nseapi import NseApi


class Strategy:

    def __init__(self):
        self.__nse_api = NseApi()
        self.name = __name__

    def run(self):
        pass

    def back_test(self, symbol, n_days):
        pass

    def get_historical_day_data_days(self, symbol, days_from_today):
        return self.__nse_api.get_historical_day_data_days(symbol=symbol, days_from_today=days_from_today)
