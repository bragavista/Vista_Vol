import os
dir_path = os.path.dirname(os.path.realpath(__file__))

import pandas as pd
import seaborn as sns

pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)
heatmap_green_red = sns.diverging_palette(160, 10, n=7,as_cmap=True)

from FetchData import EQ_Fetch_Implied_Vol
from FetchData import EQ_Fetch_Realized_Vol


eq_master_dict = {

                'Beta EM': ['IBOV Index', 'EWZ US Equity', 'RSX US Equity', 'EWW US Equity'],

                'Dev': ['SPX Index', 'SX5E Index', 'NKY Index', 'NDX Index'],

                'Asia EM' : ['NKY Index','FXI US Equity','ASHR US Equity']

            }


def implied_minus_realized (AssetList,StartDate,EndDate,Maturity,Delta,Call_Put, window):

    eq_implied_vols = EQ_Fetch_Implied_Vol.Fetch_IV_from_BBG_IVOL_DELTA(AssetList,StartDate,EndDate,Maturity,Delta,Call_Put)

    eq_realized_vols = 100*EQ_Fetch_Realized_Vol.eq_realized_vols(AssetList, StartDate, EndDate, window)

    iv_minus_rv = pd.DataFrame()

    for asset in AssetList:

        aux = eq_implied_vols[asset] - eq_realized_vols[asset].values
        aux.columns = [asset]

        iv_minus_rv = pd.concat([iv_minus_rv,aux],sort=True,axis=1)

    # iv_minus_rv = eq_implied_vols - eq_realized_vols

    return  iv_minus_rv


maturities_bbg_style = ['1M','3M','6M','1Y']

def normalized_skew (AssetList,StartDate,EndDate,Maturity,Delta_Center,Delta_Bull, Delta_Bear, Bear_cp, Center_cp, Bull_cp):

    bull_vols = EQ_Fetch_Implied_Vol.Fetch_IV_from_BBG_IVOL_DELTA(AssetList,StartDate,EndDate,Maturity,Delta_Bull,Bull_cp)

    center_vols = EQ_Fetch_Implied_Vol.Fetch_IV_from_BBG_IVOL_DELTA(AssetList,StartDate,EndDate,Maturity,Delta_Center,Center_cp)

    bear_vols = EQ_Fetch_Implied_Vol.Fetch_IV_from_BBG_IVOL_DELTA(AssetList, StartDate, EndDate, Maturity, Delta_Bear, Bear_cp)


    norm_skew = pd.DataFrame()

    for asset in AssetList:

        aux = bear_vols[asset] - bull_vols[asset].values
        aux = aux / center_vols[asset].values

        aux.columns = [asset]

        norm_skew = pd.concat([norm_skew,aux],sort=True,axis=1)


    return norm_skew




if __name__ == "__main__":

    AssetList = ['IBOV Index', 'SPX Index']
    StartDate = 20200101
    EndDate = 20201009
    Maturity = '30d'
    window = 22
    Delta = '25'
    Call_Put = 'call'

    Delta_Center = '50'
    Delta_Bull = '25'
    Delta_Bear = '25'
    Bear_cp = 'put'
    Center_cp = 'call'
    Bull_cp = 'call'

    eq_implied_vols = EQ_Fetch_Implied_Vol.Fetch_IV_from_BBG_IVOL_DELTA(AssetList,StartDate,EndDate,Maturity,Delta,Call_Put)

    iv_minus_rv = implied_minus_realized(AssetList, StartDate, EndDate, Maturity, Delta, Call_Put, window)

    norm_skew = normalized_skew(AssetList, StartDate, EndDate, Maturity, Delta_Center, Delta_Bull, Delta_Bear, Bear_cp, Center_cp, Bull_cp)

    print (norm_skew)