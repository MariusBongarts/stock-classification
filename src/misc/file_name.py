from yahoo_finance_api2 import share

intervals_to_profit = 3
take_profit = 1.06
stop_loss=1.00
periods=50
period_type=share.PERIOD_TYPE_YEAR
frequency_type=share.FREQUENCY_TYPE_DAY
frequency=1

file_name = f'frequency_type-{frequency_type}-period_type-{period_type}-itp{intervals_to_profit}-tp{take_profit}-sl{stop_loss}-period-{periods}'
