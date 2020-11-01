try:
    from Util import BloombergAPI_new as BloombergAPI
except:
    import BloombergAPI_new as BloombergAPI

import numpy as np
import datetime
from pandas.tseries.offsets import BDay
import pandas as pd

from FetchData import EQ_FetchHistoricalPrices


def eq_realized_vols(AssetList,StartDate,EndDate,window):

    EndDate_obj = datetime.datetime.strptime(str(EndDate), '%Y%m%d').date()
    StartDate_obj = datetime.datetime.strptime(str(StartDate), '%Y%m%d').date()

    offset_start_date_for_realized = (StartDate_obj - BDay(window+5)).date()

    prices = EQ_FetchHistoricalPrices.pull_price_history (AssetList,offset_start_date_for_realized,EndDate_obj)

    log_returns = (np.log(prices) - np.log(prices.shift(1))).fillna(0)

    eq_realized_vols = log_returns.rolling(window=window).std()*np.sqrt(252)

    eq_realized_vols = eq_realized_vols.dropna()

    eq_realized_vols = eq_realized_vols.loc[eq_realized_vols.index>=StartDate_obj]
    return eq_realized_vols


if __name__ == "__main__":

    StartDate = 20200618

    EndDate = 20201009

    AssetList = ["SPX Index","IBOV Index"]

    eq_realized_vols = eq_realized_vols(AssetList,StartDate,EndDate,window=22)

    print (eq_realized_vols)
