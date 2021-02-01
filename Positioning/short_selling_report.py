try:
    import Util
    from Util import BloombergAPI_new as BloombergAPI
    from Util import QuantMetrics as QuantMetrics
    from Util import EmailSender as EmailSender
    from FetchData import EQ_FetchHistoricalPrices
    print('try worked and commited from laptop2j')

except:
    import Util.BloombergAPI_new as BloombergAPI
    import Util.QuantMetrics as QuantMetrics
    import Util.EmailSender as EmailSender
    import FetchData.EQ_FetchHistoricalPrices as EQ_FetchHistoricalPrices

import pandas as pd
pd.set_option('display.max_rows', 150)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)




import numpy as np
import matplotlib.pyplot as plt
import io
import os
from datetime import datetime
StartDate = 20190101
EndDate = int(datetime.today().strftime('%Y%m%d'))

AssetList = [
                'GME US Equity',
                'AMC US Equity',
                'FIZZ US Equity',
                'NOK US Equity',
                'BBBY US Equity'
]

fields_list = [

            'SI_PERCENT_EQUITY_FLOAT',
            'SHORT_INTEREST',
            'PX_LAST',
            'SHORT_INT_RATIO',
            'EQY_FLOAT'
]


All_fields_history = EQ_FetchHistoricalPrices.pull_multiple_fields_history(AssetList=AssetList,fields_list=fields_list,StartDate=StartDate,EndDate=EndDate)


def total_short_losses (stock):
    data = All_fields_history[stock][['SHORT_INTEREST','PX_LAST']]
    short_selling_reporting_dates = data.drop_duplicates(subset=['SHORT_INTEREST'],keep='last')
    short_selling_reporting_dates['px_diff'] = short_selling_reporting_dates['PX_LAST'].diff()
    short_selling_reporting_dates['aux_short_int_shifted'] = short_selling_reporting_dates['SHORT_INTEREST'].shift(1)
    short_selling_reporting_dates['pnl_est'] = short_selling_reporting_dates['aux_short_int_shifted'] * short_selling_reporting_dates['px_diff'].values

    return short_selling_reporting_dates

