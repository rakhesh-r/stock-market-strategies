from nseapi import NseApi


class Strategy:

    def __init__(self):
        self.__nse_api = NseApi()
        self.name = __name__

    def _get_historical_day_data_days(self, symbol, days_from_today):
        return self.__nse_api.get_historical_day_data_days(symbol=symbol, days_from_today=days_from_today)

    def _get_top_gainers_above_perc(self, index, perc):
        return self.__nse_api.get_top_gainers_above_perc(index, perc)

    def _get_top_losers_below_perc(self, index, perc):
        return self.__nse_api.get_top_losers_below_perc(index, perc)
