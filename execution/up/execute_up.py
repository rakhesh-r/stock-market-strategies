from strategies.up import UltaPulta, PreviousDayFactor, ChangeType, TargetType
import xlsxwriter
import json

__up = UltaPulta(percentage_threshold=4.8, sl_percentage=1.0, change_type=ChangeType.PREV_CLOSE_TO_CLOSE,
                 target_type=TargetType.TARGET_50_PERC,
                 previous_day_factor=PreviousDayFactor.PREVIOUS_DAY_HIGH_OR_LOW)


def store_todays_up_eligible_stocks(indices: []):
    out = __up.get_selected_stock_list(indices)
    symobls = []
    with open('../../dumps/up/up_eligible_stocks_details.json', 'w') as fp:
        json.dump(out, fp)
    for index in out:
        for stock in out[index]["tg"]:
            if stock["symbol"] not in symobls:
                symobls.append(stock["symbol"])
        for stock in out[index]["tl"]:
            if stock["symbol"] not in symobls:
                symobls.append(stock["symbol"])
    with open('../../dumps/up/up_eligible_stock_symbols.json', 'w') as fp:
        json.dump(symobls, fp)


def backtest_stocks():
    up = UltaPulta(percentage_threshold=4.8, sl_percentage=2.0, change_type=ChangeType.PREV_CLOSE_TO_CLOSE,
                   target_type=TargetType.TARGET_OPEN,
                   previous_day_factor=PreviousDayFactor.PREVIOUS_DAY_HIGH_OR_LOW)
    backtest_result = []
    with open('../../dumps/up/up_eligible_stock_symbols.json', 'r') as fp:
        symbols = json.load(fp)
    for symbol in symbols:
        backtest_result.extend(up.back_test(symbol, 60))
    workbook = xlsxwriter.Workbook("../../dumps/up/backtest_2_SL.xlsx")
    sheet = workbook.add_worksheet()
    # column headers
    sheet_columns = [{'key': 'date', 'value': 'Date'},
                     {'key': 'symbol', 'value': 'Symbol'},
                     {'key': 'is_eligible', 'value': 'Is Eligible'},
                     {'key': 'is_order_executed', 'value': 'Order Executed'},
                     {'key': 'profit_booked_at', 'value': 'Profit Booked at'},
                     {'key': 'profit_booked_at_perc', 'value': 'Profit Booked at Percentage'},
                     {'key': 'market_order_price', 'value': 'Order price'},
                     {'key': 'market_order_sl', 'value': 'Stop Loss'}]
    for i in range(len(sheet_columns)):
        sheet.write(0, i, sheet_columns[i]["value"])
    # sheet content
    for i in range(len(backtest_result)):
        for j in range(len(sheet_columns)):
            sheet.write(i + 1, j, backtest_result[i][sheet_columns[j]["key"]])
    workbook.close()


#store_todays_up_eligible_stocks(["NIFTY 500", "NIFTY MIDSMALLCAP 400"])

backtest_stocks()
