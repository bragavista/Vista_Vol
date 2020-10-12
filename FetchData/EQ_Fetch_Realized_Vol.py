try:
    from Util import BloombergAPI_new as BloombergAPI
except:
    import BloombergAPI_new as BloombergAPI

import numpy as np

from FetchData import EQ_FetchHistoricalPrices


def eq_realized_vols(AssetList,StartDate,EndDate,window):

    prices = EQ_FetchHistoricalPrices.pull_price_history (AssetList,StartDate,EndDate)

    log_returns = (np.log(prices) - np.log(prices.shift(1))).fillna(0)

    eq_realized_vols = log_returns.rolling(window=window).std()*np.sqrt(252)

    return eq_realized_vols


if __name__ == "__main__":

    StartDate = 20200618

    EndDate = 20201009

    AssetList = ["SPX Index","IBOV Index"]

    eq_realized_vols = eq_realized_vols(AssetList,StartDate,EndDate,window=22)

    print (eq_realized_vols)
