import BloombergAPI_new as BloombergAPI
import pandas as pd
import numpy as np
from datetime import date
import datetime
import dateutil.relativedelta
from scipy import stats
pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)


fx_master_dict = {
                'High Beta EM': ['USDBRL','USDMXN','USDZAR','USDTRY','USDRUB'],
                'Developed': ['EURUSD','GBPUSD','EURGBP','USDJPY','EURCHF','AUDUSD','USDCAD'],
                'Scandies': ['EURNOK','EURSEK','NOKSEK','USDSEK','USDNOK'],
                'CEEMEA' : ['EURPLN','EURCZK','USDILS'],
                'Asia EM' : ['USDTWD','USDINR']
            }

maturities_bbg_style = ['2W','1M','3M','6M','1Y']


def crete_bbg_list (fx_master_dict = fx_master_dict):

    implied_dict = dict()
    real_dict = dict()

    bloomberg_list = list()

    for region in fx_master_dict.keys():

        for fx_pair in fx_master_dict[region]:

            implied_dict[fx_pair] = dict()
            real_dict[fx_pair] = dict()

            for mat in maturities_bbg_style:

                implied_dict[fx_pair][mat]  = fx_pair+'V'+mat+' Curncy'
                real_dict[fx_pair][mat]     = fx_pair+'H'+mat+' Curncy'
                bloomberg_list = bloomberg_list +[fx_pair+'V'+mat+' Curncy' , fx_pair+'H'+mat+' Curncy']


    return implied_dict,real_dict,bloomberg_list



def fx_fetch_implied_bbg(bloomberg_list,StartDate,EndDate):

    blp = BloombergAPI.BLPInterface()
    raw_data = blp.historicalRequest(bloomberg_list, "px_last", StartDate, EndDate)
    raw_data.columns = list(raw_data)

    return raw_data

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

    return Implied_minus_Realized_Percentiles






if __name__ == "__main__":

    print('hello, calculating FX iv and iv-rv data now')
    EndDate = date.today()
    StartDate = EndDate - dateutil.relativedelta.relativedelta(months=1)
    implied_dict,real_dict,bloomberg_list = crete_bbg_list (fx_master_dict = fx_master_dict)
    raw_data = fx_fetch_implied_bbg(bloomberg_list,StartDate,EndDate)



    Implied_Percentiles = treat_raw_data_iv_pctle(implied_dict, raw_data)
    print(Implied_Percentiles)

    Implied_minus_Realized_Percentiles = treat_raw_data_iv_minus_rv_pctle(implied_dict, real_dict, raw_data)
    print(Implied_minus_Realized_Percentiles)





