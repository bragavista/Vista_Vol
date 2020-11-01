import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.colors as mcolors
from scipy import stats


fx_master_dict = {
                'Beta EM': ['USDBRL','USDMXN','USDZAR','USDTRY','USDRUB'],
                'Dev': ['EURUSD','GBPUSD','EURGBP','USDJPY','EURCHF','USDCHF','AUDUSD','USDCAD'],
                'Scandies': ['EURNOK','EURSEK','NOKSEK','USDSEK','USDNOK'],
                'CEEMEA' : ['EURPLN','EURCZK','USDILS'],
                'Asia EM' : ['USDTWD','USDINR','USDCNH']
            }


eq_master_dict = {
                'EM Local': ['IBOV Index','HSCEI Index','KOSPI Index'],
                'EM ETF': ['EEM US Equity', 'EWZ US Equity', 'FXI US Equity','EWW US Equity'],
                'US': ['SPX Index','NDX Index','RTY Index'],
                'DM ': ['SX5E Index','NKY Index'],
            }


def asset_to_region(asset,master_dict):

    region_final ='no_region_mapped'

    for region in master_dict.keys():

        if asset in master_dict[region]:
            region_final = region

    return region_final

def corr_matrix_from_prices (PricesDataframe):

    returns = PricesDataframe.pct_change().fillna(0)

    corr_matrix = returns.corr(method='pearson')

    return corr_matrix

def corr_matrix_masking_and_plotting (corr_matrix):
    cdict = {'red': ((0.0, 0.0, 0.0),
                     (0.5, 0.0, 0.0),
                     (1.0, 1.0, 1.0)),
             'blue': ((0.0, 0.0, 0.0),
                      (1.0, 0.0, 0.0)),
             'green': ((0.0, 0.0, 1.0),
                       (0.5, 0.0, 0.0),
                       (1.0, 0.0, 0.0))}

    cmap = mcolors.LinearSegmentedColormap(
        'my_colormap', cdict, 100)

    # cmap = sns.palplot(sns.diverging_palette(10, 220, sep=80, n=7))

    matrix = np.triu(corr_matrix)

    sns.heatmap(corr_matrix, annot=True, mask=matrix,cmap=cmap,linewidths=3, linecolor='white',cbar=False)

    return

def treat_raw_data_iv_pctle (implied_dict,raw_data):

    Implied_Percentiles = pd.DataFrame()

    Implied_Vols_list = list()

    for fx_pair in implied_dict:
        for mat in implied_dict[fx_pair]:
            Implied_Vols_list.append(implied_dict[fx_pair][mat])

    all_implied_vol_time_series = raw_data[Implied_Vols_list]


    for fx_pair in implied_dict.keys():

        list_of_mats = list(implied_dict[fx_pair].keys())

        Implied_Percentiles_fxpair = pd.DataFrame()

        for mat in list_of_mats:

            time_series = all_implied_vol_time_series[implied_dict[fx_pair][mat]]
            last_value = round(time_series.tail(1)[0],1)
            last_percentile = round(stats.percentileofscore(time_series, last_value),0)
            aux = pd.DataFrame(index=[fx_pair],columns=[mat+' last',mat+' pctle'],data=[[last_value,last_percentile]])
            Implied_Percentiles_fxpair = pd.concat([Implied_Percentiles_fxpair,aux],axis=1,sort=True)

        Implied_Percentiles = Implied_Percentiles.append(Implied_Percentiles_fxpair)



    region_aux = pd.DataFrame(data=[asset_to_region(fx_pair,fx_master_dict) for fx_pair in Implied_Percentiles.index],columns=['Region'],index=Implied_Percentiles.index)
    Implied_Percentiles = pd.concat([region_aux,Implied_Percentiles],axis=1,sort=False)
    Implied_Percentiles = Implied_Percentiles.rename_axis('Implieds')


    return Implied_Percentiles

def treat_raw_data_iv_minus_rv_pctle (implied_dict,real_dict,raw_data):

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

    region_aux = pd.DataFrame(data=[asset_to_region(fx_pair,fx_master_dict) for fx_pair in Implied_minus_Realized_Percentiles.index],columns=['Region'],index=Implied_minus_Realized_Percentiles.index)


    Implied_minus_Realized_Percentiles = pd.concat([region_aux,Implied_minus_Realized_Percentiles],axis=1,sort=False)

    Implied_minus_Realized_Percentiles = Implied_minus_Realized_Percentiles.rename_axis('Implied - Real')

    return Implied_minus_Realized_Percentiles

