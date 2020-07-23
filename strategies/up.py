from strategies.strategy import Strategy
import enum
# import json


class ChangeType(enum.Enum):
    PREV_CLOSE_TO_CLOSE = 1
    LOW_TO_HIGH = 2
    OPEN_TO_CLOSE = 3


class TargetType(enum.Enum):
    TARGET_OPEN = 1
    TARGET_50_PERC = 2


class PreviousDayFactor(enum.Enum):
    PREVIOUS_DAY_CLOSE = 1
    PREVIOUS_DAY_HIGH_OR_LOW = 2


class DayTrend(enum.Enum):
    BULLISH = 1
    BEARISH = 2
    NEUTRAL = 3


class UltaPulta(Strategy):

    def __init__(self):
        # Calling super init
        super().__init__()
        # name gets overridden
        self.name = __name__
        self.change_type = ChangeType.PREV_CLOSE_TO_CLOSE
        self.target_type = TargetType.TARGET_OPEN
        self.previous_day_factor = PreviousDayFactor.PREVIOUS_DAY_HIGH_OR_LOW
        self.__CHANGE_PERC = 5.0
        self.__SL_PERC = 1.0

    def run(self):
        print("Running", self.name)

    def back_test(self, symbol, n_days):
        # you get history data in descending order
        hist_data = self.get_historical_day_data_days(symbol, n_days)
        if not hist_data or len(hist_data) == 0:
            return
        response_json = []
        for i in range(len(hist_data) - 1):
            response_entity = {"date": hist_data[i]["CH_TIMESTAMP"], "symbol": hist_data[i]["CH_SYMBOL"]}
            change = self._get_change_perc(hist_data[i + 1])
            day_trend = self._get_market_day_trend(change)
            # Consider only change with 5 percent or above/below for selling/buying
            if self._check_for_eligibility(change, day_trend, hist_data[i], hist_data[i + 1]):
                is_eligible = True
                market_order_price = self._get_market_order_price(trend=day_trend,
                                                                  hist_data_previous_day=hist_data[i + 1])
                market_order_sl = self._get_sl(market_order_price, day_trend)
                is_order_executed = self._check_price_in_range(market_order_price, hist_data[i]["CH_TRADE_HIGH_PRICE"],
                                                               hist_data[i]["CH_TRADE_LOW_PRICE"])
                if is_order_executed:
                    is_sl_hit = self._check_price_in_range(market_order_sl, hist_data[i]["CH_TRADE_HIGH_PRICE"],
                                                           hist_data[i]["CH_TRADE_LOW_PRICE"])
                    if not is_sl_hit:
                        if self.target_type == TargetType.TARGET_OPEN:
                            profit_booked_at = hist_data[i]["CH_LAST_TRADED_PRICE"]
                        else:
                            profit_booked_at = (hist_data[i]["CH_TRADE_LOW_PRICE"] + hist_data[i][
                                "CH_TRADE_HIGH_PRICE"]) / 2
                        profit_booked_at_perc = round(
                            abs(profit_booked_at - market_order_price) / market_order_price * 100, 2)
                    else:
                        profit_booked_at_perc = -1 * self.__SL_PERC
                else:
                    is_order_executed = False
                    profit_booked_at = 0
                    profit_booked_at_perc = 0
            else:
                is_order_executed = False
                profit_booked_at = 0
                profit_booked_at_perc = 0
                is_eligible = False
                market_order_price = 0
                market_order_sl = 0
            response_entity["is_order_executed"] = is_order_executed
            response_entity["profit_booked_at"] = profit_booked_at
            response_entity["profit_booked_at_perc"] = profit_booked_at_perc
            response_entity["is_eligible"] = is_eligible
            response_entity["market_order_price"] = market_order_price
            response_entity["market_order_sl"] = market_order_sl
            response_json.append(response_entity)
        return response_json

    def _get_change_perc(self, data_today):
        if self.change_type == ChangeType.PREV_CLOSE_TO_CLOSE:
            original_number = data_today["CH_PREVIOUS_CLS_PRICE"]
            new_number = data_today["CH_LAST_TRADED_PRICE"]
        if self.change_type == ChangeType.LOW_TO_HIGH:
            if data_today["CH_OPENING_PRICE"] < data_today["CH_CLOSING_PRICE"]:
                original_number = data_today["CH_TRADE_LOW_PRICE"]
                new_number = data_today["CH_TRADE_HIGH_PRICE"]
            else:
                original_number = data_today["CH_TRADE_HIGH_PRICE"]
                new_number = data_today["CH_TRADE_LOW_PRICE"]
        if self.change_type == ChangeType.OPEN_TO_CLOSE:
            original_number = data_today["CH_OPENING_PRICE"]
            new_number = data_today["CH_CLOSING_PRICE"]
        change_perc = ((new_number - original_number) / original_number) * 100
        return round(change_perc, 2)

    def _check_for_eligibility(self, change_perc, trend, hist_data_day, hist_data_previous_day):
        if self.previous_day_factor == PreviousDayFactor.PREVIOUS_DAY_CLOSE:
            previous_day_price = hist_data_previous_day["CH_PREVIOUS_CLS_PRICE"]
        if self.previous_day_factor == PreviousDayFactor.PREVIOUS_DAY_HIGH_OR_LOW:
            if trend == DayTrend.BULLISH:
                previous_day_price = hist_data_previous_day["CH_TRADE_HIGH_PRICE"]
            if trend == DayTrend.BEARISH:
                previous_day_price = hist_data_previous_day["CH_TRADE_LOW_PRICE"]
        if trend == DayTrend.BULLISH and change_perc > self.__CHANGE_PERC and hist_data_day[
            "CH_OPENING_PRICE"] >= previous_day_price:
            return True
        if trend == DayTrend.BEARISH and change_perc < self.__CHANGE_PERC and hist_data_day[
            "CH_OPENING_PRICE"] <= previous_day_price:
            return True

    def _get_sl(self, market_order_price, trend):
        sl_points = self.__SL_PERC * market_order_price / 100
        if trend == DayTrend.BULLISH:
            sl = market_order_price + sl_points
        if trend == DayTrend.BEARISH:
            sl = market_order_price - sl_points
        return round(sl, 2)

    @staticmethod
    def _get_market_order_price(trend, hist_data_previous_day):
        if trend == DayTrend.BULLISH:
            return hist_data_previous_day["CH_TRADE_HIGH_PRICE"]
        if trend == DayTrend.BEARISH:
            return hist_data_previous_day["CH_TRADE_LOW_PRICE"]

    @staticmethod
    def _get_market_day_trend(change):
        if change > 0:
            return DayTrend.BULLISH
        if change < 0:
            return DayTrend.BEARISH
        return DayTrend.NEUTRAL

    @staticmethod
    def _check_price_in_range(market_order_price, left, right):
        if left < right:
            min_val = left
            max_val = right
        else:
            min_val = right
            max_val = left
        return min_val <= market_order_price <= max_val

# # Emergency testing
# #
# #
# up = UltaPulta()
# up.back_test('AXISBANK', 2)
# up = UltaPulta()
# jsonString = """{"_id":"5f1192fecef9350008a52153","CH_SYMBOL":"BPCL","CH_SERIES":"EQ","CH_MARKET_TYPE":"N",
# "CH_TRADE_HIGH_PRICE":447.4,"CH_TRADE_LOW_PRICE":392,"CH_OPENING_PRICE":404.5,"CH_CLOSING_PRICE":443.8,
# "CH_LAST_TRADED_PRICE":442.85,"CH_PREVIOUS_CLS_PRICE":393.9,"CH_TOT_TRADED_QTY":53842324,
# "CH_TOT_TRADED_VAL":23022309394.2,"CH_52WEEK_HIGH_PRICE":549,"CH_52WEEK_LOW_PRICE":252,"CH_TOTAL_TRADES":511790,
# "CH_ISIN":"INE029A01011","CH_TIMESTAMP":"2020-07-17","TIMESTAMP":"2020-07-16T18:30:00.000Z",
# "createdAt":"2020-07-17T12:01:02.375Z","updatedAt":"2020-07-17T12:01:02.375Z","__v":0,"VWAP":427.59,
# "mTIMESTAMP":"17-Jul-2020"} """
# dic = json.loads(jsonString)
# print("Change", up._get_change_perc(dic))
#
# jsonString2 = """[{"_id":"5f1192fecef9350008a52153","CH_SYMBOL":"BPCL","CH_SERIES":"EQ","CH_MARKET_TYPE":"N",
# "CH_TRADE_HIGH_PRICE":429.3,"CH_TRADE_LOW_PRICE":387,"CH_OPENING_PRICE":389.5,"CH_CLOSING_PRICE":409.8,
# "CH_LAST_TRADED_PRICE":409.8,"CH_PREVIOUS_CLS_PRICE":399.9,"CH_TOT_TRADED_QTY":53842324,
# "CH_TOT_TRADED_VAL":23022309394.2,"CH_52WEEK_HIGH_PRICE":549,"CH_52WEEK_LOW_PRICE":252,"CH_TOTAL_TRADES":511790,
# "CH_ISIN":"INE029A01011","CH_TIMESTAMP":"2020-07-17","TIMESTAMP":"2020-07-16T18:30:00.000Z",
# "createdAt":"2020-07-17T12:01:02.375Z","updatedAt":"2020-07-17T12:01:02.375Z","__v":0,"VWAP":427.59,
# "mTIMESTAMP":"17-Jul-2020"},{"_id":"5f1098744fc18a00089d0ff2","CH_SYMBOL":"BPCL","CH_SERIES":"EQ",
# "CH_MARKET_TYPE":"N","CH_TRADE_HIGH_PRICE":452.1,"CH_TRADE_LOW_PRICE":394.3,"CH_OPENING_PRICE":449.2,
# "CH_CLOSING_PRICE":399.9,"CH_LAST_TRADED_PRICE":399.9,"CH_PREVIOUS_CLS_PRICE":439.6,"CH_TOT_TRADED_QTY":13308018,
# "CH_TOT_TRADED_VAL":5080337358.5,"CH_52WEEK_HIGH_PRICE":549,"CH_52WEEK_LOW_PRICE":252,"CH_TOTAL_TRADES":138380,
# "CH_ISIN":"INE029A01011","CH_TIMESTAMP":"2020-07-16","TIMESTAMP":"2020-07-15T18:30:00.000Z",
# "createdAt":"2020-07-16T18:12:04.781Z","updatedAt":"2020-07-16T18:12:04.781Z","__v":0,"VWAP":381.75,
# "mTIMESTAMP":"16-Jul-2020"},{"_id":"5f111ca7cc94cd0009f48aef","CH_SYMBOL":"BPCL","CH_SERIES":"EQ",
# "CH_MARKET_TYPE":"N","CH_TRADE_HIGH_PRICE":442.35,"CH_TRADE_LOW_PRICE":404.2,"CH_OPENING_PRICE":409,
# "CH_CLOSING_PRICE":439.6,"CH_LAST_TRADED_PRICE":439.6,"CH_PREVIOUS_CLS_PRICE":399.3,"CH_TOT_TRADED_QTY":4903936,
# "CH_TOT_TRADED_VAL":1834984914.95,"CH_52WEEK_HIGH_PRICE":549,"CH_52WEEK_LOW_PRICE":252,"CH_TOTAL_TRADES":57972,
# "CH_ISIN":"INE029A01011","CH_TIMESTAMP":"2020-07-15","TIMESTAMP":"2020-07-14T18:30:00.000Z",
# "createdAt":"2020-07-17T03:36:07.868Z","updatedAt":"2020-07-17T03:36:07.868Z","__v":0,"VWAP":374.19,
# "mTIMESTAMP":"15-Jul-2020"},{"_id":"5f0debd44826170008aa195a","CH_SYMBOL":"BPCL","CH_SERIES":"EQ",
# "CH_MARKET_TYPE":"N","CH_TRADE_HIGH_PRICE":400.9,"CH_TRADE_LOW_PRICE":392.1,"CH_OPENING_PRICE":394.1,
# "CH_CLOSING_PRICE":399.3,"CH_LAST_TRADED_PRICE":399.3,"CH_PREVIOUS_CLS_PRICE":409.95,"CH_TOT_TRADED_QTY":4741344,
# "CH_TOT_TRADED_VAL":1794634962.1,"CH_52WEEK_HIGH_PRICE":549,"CH_52WEEK_LOW_PRICE":252,"CH_TOTAL_TRADES":76901,
# "CH_ISIN":"INE029A01011","CH_TIMESTAMP":"2020-07-14","TIMESTAMP":"2020-07-13T18:30:00.000Z",
# "createdAt":"2020-07-14T17:31:00.490Z","updatedAt":"2020-07-14T17:31:00.490Z","__v":0,"VWAP":378.51,
# "mTIMESTAMP":"14-Jul-2020"},{"_id":"5f0c4ce078363500084cab18","CH_SYMBOL":"BPCL","CH_SERIES":"EQ",
# "CH_MARKET_TYPE":"N","CH_TRADE_HIGH_PRICE":411.2,"CH_TRADE_LOW_PRICE":384.45,"CH_OPENING_PRICE":389.3,
# "CH_CLOSING_PRICE":409.95,"CH_LAST_TRADED_PRICE":409.95,"CH_PREVIOUS_CLS_PRICE":401,"CH_TOT_TRADED_QTY":5139428,
# "CH_TOT_TRADED_VAL":1957300768.8,"CH_52WEEK_HIGH_PRICE":549,"CH_52WEEK_LOW_PRICE":252,"CH_TOTAL_TRADES":81797,
# "CH_ISIN":"INE029A01011","CH_TIMESTAMP":"2020-07-13","TIMESTAMP":"2020-07-12T18:30:00.000Z",
# "createdAt":"2020-07-13T12:00:32.451Z","updatedAt":"2020-07-13T12:00:32.451Z","__v":0,"VWAP":380.84,
# "mTIMESTAMP":"13-Jul-2020"},{"_id":"5f111d35da8bb90009dbd644","CH_SYMBOL":"BPCL","CH_SERIES":"EQ",
# "CH_MARKET_TYPE":"N","CH_TRADE_HIGH_PRICE":404.5,"CH_TRADE_LOW_PRICE":379.35,"CH_OPENING_PRICE":382,
# "CH_CLOSING_PRICE":401,"CH_LAST_TRADED_PRICE":401,"CH_PREVIOUS_CLS_PRICE":376.75,"CH_TOT_TRADED_QTY":5883057,
# "CH_TOT_TRADED_VAL":2202086717.65,"CH_52WEEK_HIGH_PRICE":549,"CH_52WEEK_LOW_PRICE":252,"CH_TOTAL_TRADES":92688,
# "CH_ISIN":"INE029A01011","CH_TIMESTAMP":"2020-07-10","TIMESTAMP":"2020-07-09T18:30:00.000Z",
# "createdAt":"2020-07-17T03:38:29.639Z","updatedAt":"2020-07-17T03:38:29.639Z","__v":0,"VWAP":374.31,
# "mTIMESTAMP":"10-Jul-2020"}]""" dic2 = json.loads(jsonString2) print(dic2) print(up.back_test(symbol='INFY',
# n_days=10)) # # # Emergency testing
