import os
dir_path = os.path.dirname(os.path.realpath(__file__))

import pandas as pd
import seaborn as sns
from scipy import stats


pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)
heatmap_green_red = sns.diverging_palette(160, 10, n=7,as_cmap=True)

from FetchData import EQ_Fetch_Implied_Vol
from FetchData import EQ_Fetch_Realized_Vol
from Util import QuantMetrics


def implied_minus_realized (AssetPairList,StartDate,EndDate,Maturity,Delta,Call_Put, window):

    #this function pulls implied minus realized for a pair of asse

    eq_implied_vols = EQ_Fetch_Implied_Vol.Fetch_IV_from_BBG_IVOL_DELTA(AssetPairList,StartDate,EndDate,Maturity,Delta,Call_Put)

    eq_realized_vols = 100*EQ_Fetch_Realized_Vol.eq_realized_vols(AssetList, StartDate, EndDate, window)

    iv_minus_rv = pd.DataFrame()

    for asset in AssetList:

        aux = eq_implied_vols[asset] - eq_realized_vols[asset].values
        aux.columns = [asset]

        iv_minus_rv = pd.concat([iv_minus_rv,aux],sort=True,axis=1)

    # iv_minus_rv = eq_implied_vols - eq_realized_vols

    return  iv_minus_rv

def implied_minus_realized_dfdatasource (AssetList,all_eq_implied_vols,all_eq_hist_vols,Implied_Real_Term_mapping = {'30d':  22, '60d':  44,'90d':  66,'180d': 126,'360d': 252,'720d': 504}):

    #this function pulls implied minus realized for a pair of asse
    Implied_Tenors = list(Implied_Real_Term_mapping.keys())
    realized_windows = list(Implied_Real_Term_mapping.values())
    #
    # all_eq_implied_vols = fetch_eq_imp_vol_multiple_tenors(AssetList, StartDate, EndDate, Delta, Call_Put, Implied_Tenors=Implied_Tenors)
    # all_eq_hist_vols = fetch_eq_hist_vol_multiple_tenors(AssetList, StartDate, EndDate, realized_windows=realized_windows)

    iv_minus_rv_final = pd.DataFrame()

    for asset in AssetList:
        iv_minus_rv = pd.DataFrame()

        for imp_real_pair in Implied_Real_Term_mapping.keys():
            tenor = imp_real_pair
            real_wdw = Implied_Real_Term_mapping[tenor]

            imp =  all_eq_implied_vols[tenor][asset]
            imp.columns=['aux']
            real = all_eq_hist_vols[real_wdw][asset]
            real.columns=['aux']

            aux = imp-real

            new_columns = pd.MultiIndex.from_arrays([[asset],['iv-rv'],[tenor],[real_wdw]],names=('Asset','iv-rv','tenor','real_wdw'))
            aux.columns = new_columns

            iv_minus_rv = pd.concat([iv_minus_rv,aux],sort=True,axis=1)

        iv_minus_rv_final = pd.concat([iv_minus_rv_final, iv_minus_rv], sort=True, axis=1)

    return  iv_minus_rv_final

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

def fetch_eq_imp_vol_multiple_tenors (AssetList,StartDate,EndDate,Delta,Call_Put, Implied_Tenors=['30d', '60d', '90d', '180d', '360d', '720d']):


    all_eq_implied_vols = dict()

    for mat in Implied_Tenors:

        eq_implied_vols = EQ_Fetch_Implied_Vol.Fetch_IV_from_BBG_IVOL_DELTA(AssetList,StartDate,EndDate,mat,Delta,Call_Put)

        all_eq_implied_vols[mat] = eq_implied_vols

    return all_eq_implied_vols

def fetch_eq_hist_vol_multiple_tenors (AssetList,StartDate,EndDate,realized_windows=[22,44]):


    all_hist_implied_vols = dict()

    for window in realized_windows:

        eq_realized_vols = 100 * EQ_Fetch_Realized_Vol.eq_realized_vols(AssetList, StartDate, EndDate, window)

        all_hist_implied_vols[window] = eq_realized_vols

    return all_hist_implied_vols





def treat_iv_to_percentile (all_eq_implied_vols,window=252):

    Implied_Percentiles_eqvol = pd.DataFrame()

    for mat in all_eq_implied_vols.keys():

        time_series = all_eq_implied_vols[mat]

        Implied_Percentiles = pd.DataFrame()

        for asset in time_series:

            time_series_perasset = time_series[asset]

            last_value = round(time_series_perasset.tail(1)[0],1)

            last_percentile = round(stats.percentileofscore(time_series_perasset, last_value),0)

            aux = pd.DataFrame(index=[asset[0]],columns=[mat+' last',mat+' pctle'],data=[[last_value,last_percentile]])
            Implied_Percentiles = Implied_Percentiles.append(aux)

################ TODO HERE

        Implied_Percentiles_eqvol = pd.concat([Implied_Percentiles_eqvol,Implied_Percentiles],axis=1,sort=True)

    region_aux = pd.DataFrame(data=[QuantMetrics.asset_to_region(asset,QuantMetrics.eq_master_dict) for asset in Implied_Percentiles_eqvol.index],columns=['Region'],index=Implied_Percentiles_eqvol.index)
    Implied_Percentiles_eqvol['region'] = region_aux

    return Implied_Percentiles_eqvol


def treat_raw_data_iv_minus_rv_pctle (all_eq_implied_vols,real_dict,raw_data):

    Implied_minus_Realized_Percentiles = pd.DataFrame()

    Implied_Vols_list = list()
    Real_vols_list = list()


    for fx_pair in implied_dict:
        for mat in implied_dict[fx_pair]:
            Implied_Vols_list.append(implied_dict[fx_pair][mat])
            Real_vols_list.append(real_dict[fx_pair][mat])

    all_implied_vol_time_series = raw_data[Implied_Vols_list]
    all_realized_vol_time_series = raw_data[Real_vols_list]


    for fx_pair in implied_dict.keys():

        list_of_mats = list(implied_dict[fx_pair].keys())

        Implied_Percentiles_iv_rv = pd.DataFrame()

        for mat in list_of_mats:
            time_series_iv = all_implied_vol_time_series[implied_dict[fx_pair][mat]]
            time_series_rv = all_realized_vol_time_series[real_dict[fx_pair][mat]]
            iv_rv_diff = time_series_iv - time_series_rv

            last_value = round(iv_rv_diff.tail(1)[0],1)
            last_percentile = round(stats.percentileofscore(iv_rv_diff, last_value),0)

            aux = pd.DataFrame(index=[fx_pair],columns=[mat+' last',mat+' pctle'],data=[[last_value,last_percentile]])
            Implied_Percentiles_iv_rv = pd.concat([Implied_Percentiles_iv_rv,aux],axis=1,sort=True)

        Implied_minus_Realized_Percentiles = Implied_minus_Realized_Percentiles.append(Implied_Percentiles_iv_rv)

    region_aux = pd.DataFrame(data=[QuantMetrics.asset_to_region(fx_pair) for fx_pair in Implied_Percentiles.index],columns=['Region'],index=Implied_Percentiles.index)
    Implied_minus_Realized_Percentiles = pd.concat([region_aux,Implied_minus_Realized_Percentiles],axis=1,sort=False)

    Implied_minus_Realized_Percentiles = Implied_minus_Realized_Percentiles.rename_axis('Implied - Real')

    return Implied_minus_Realized_Percentiles


if __name__ == "__main__":

    AssetList = ['IBOV Index', 'SPX Index','SX5E Index']
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


    Implied_Real_Term_mapping = {
                                    '30d':  22,
                                    '60d':  44,
                                    '90d':  66,
                                    '180d': 126,
                                    '360d': 252,
                                    '720d': 504
    }


    all_eq_implied_vols = fetch_eq_imp_vol_multiple_tenors(AssetList, StartDate, EndDate, Delta, Call_Put,Implied_Tenors=['30d', '60d', '90d', '180d', '360d', '720d'])

    all_eq_hist_vols = fetch_eq_hist_vol_multiple_tenors (AssetList,StartDate,EndDate, realized_windows = [22, 44, 66, 126, 252, 504])


    all_eq_iv_minus_rv = implied_minus_realized_dfdatasource(AssetList, all_eq_implied_vols,all_eq_hist_vols,StartDate,
                                        Implied_Real_Term_mapping={'30d': 22, '60d': 44, '90d': 66, '180d': 126,
                                                                   '360d': 252, '720d': 504})

    iv_minus_rv = implied_minus_realized(AssetList, StartDate, EndDate, Maturity, Delta, Call_Put, window)

    iv_minus_rv2 = implied_minus_realized_dfdatasource(AssetList, StartDate, EndDate, Maturity,Implied_Real_Term_mapping )



    #
    # all_real_vols = fe
    #
    # eq_implied_vol_percentiles = treat_iv_to_percentile(all_eq_implied_vols,window=252)
    #
    #
    # print(eq_implied_vol_percentiles)

    # eq_implied_vols = EQ_Fetch_Implied_Vol.Fetch_IV_from_BBG_IVOL_DELTA(AssetList,StartDate,EndDate,Maturity,Delta,Call_Put)
    # print(eq_implied_vols)
    #
    # iv_minus_rv = implied_minus_realized(AssetList, StartDate, EndDate, Maturity, Delta, Call_Put, window)
    # print(iv_minus_rv)
    #
    # norm_skew = normalized_skew(AssetList, StartDate, EndDate, Maturity, Delta_Center, Delta_Bull, Delta_Bear, Bear_cp, Center_cp, Bull_cp)
    #
    # print (norm_skew)