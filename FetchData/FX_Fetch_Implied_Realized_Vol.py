import BloombergAPI_new as BloombergAPI
import pandas as pd
import numpy as np
from datetime import date
import datetime
import dateutil.relativedelta
from scipy import stats


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
            last_value = time_series.tail(1)[0]
            last_percentile = stats.percentileofscore(time_series, last_value)

            aux = pd.DataFrame(index=[fx_pair],columns=[mat+' last',mat+' pctle'],data=[[last_value,last_percentile]])
            Implied_Percentiles_fxpair = pd.concat([Implied_Percentiles_fxpair,aux],axis=1,sort=True)

        Implied_Percentiles = Implied_Percentiles.append(Implied_Percentiles_fxpair)
    #
    #
    # for implied_vol_series in all_implied_vol_time_series.columns:
    #     time_series = all_implied_vol_time_series[implied_vol_series]
    #     tested_value = time_series.tail(1)[0]
    #     last_percentile = stats.percentileofscore(time_series,tested_value)


    return Implied_Percentiles









if __name__ == "__main__":

    EndDate = date.today()
    StartDate = EndDate - dateutil.relativedelta.relativedelta(months=1)
    implied_dict,real_dict,bloomberg_list = crete_bbg_list (fx_master_dict = fx_master_dict)
    raw_data = fx_fetch_implied_bbg(bloomberg_list,StartDate,EndDate)