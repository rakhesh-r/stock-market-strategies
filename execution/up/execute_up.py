from strategies.up import UltaPulta, PreviousDayFactor, ChangeType, TargetType
import xlsxwriter
import json


# Previous day after market close
def store_todays_up_eligible_stocks(up: UltaPulta, indices: []):
    out = up.get_selected_stock_list_for_next_day(indices)
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


# Previous day after market close
def backtest_stocks(up: UltaPulta):
    backtest_result = []
    with open('../../dumps/up/up_eligible_stock_symbols.json', 'r') as fp:
        symbols = json.load(fp)
    for symbol in symbols:
        backtest_result.extend(up.back_test(symbol, 60))
    workbook = xlsxwriter.Workbook("../../dumps/up/backtest_5_2_SL.xlsx")
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


# Present day after 9:15
def select_stocks_based_on_gap_up(up: UltaPulta):
    with open('../../dumps/up/up_eligible_stocks_details.json', 'r') as fp:
        previous_day_data = json.load(fp)
    selected_stocks = up.filter_previous_day_stocks(previous_day_data)
    with open('../../dumps/up/up_selected_stocks_order_details.json', 'w') as fp:
        json.dump(selected_stocks, fp)
    print(selected_stocks)


ulta_pulta = UltaPulta(percentage_threshold=5.0, sl_percentage=2, change_type=ChangeType.PREV_CLOSE_TO_CLOSE,
                       target_type=TargetType.TARGET_OPEN,
                       previous_day_factor=PreviousDayFactor.PREVIOUS_DAY_HIGH_OR_LOW)
# store_todays_up_eligible_stocks(ulta_pulta, ["NIFTY 500", "NIFTY MIDSMALLCAP 400"])

# backtest_stocks(ulta_pulta)

select_stocks_based_on_gap_up(ulta_pulta)
