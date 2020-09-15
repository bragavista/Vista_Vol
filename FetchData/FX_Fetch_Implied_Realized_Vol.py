import BloombergAPI_new as BloombergAPI
import pandas as pd
import numpy as np
from datetime import date
import datetime
import dateutil.relativedelta

fx_master_dict = {
                # 'High Beta EM': ['USDBRL','USDMXN','USDZAR','USDTRY','USDRUB'],
                'Developed': ['EURUSD','GBPUSD','EURGBP','USDJPY','EURCHF','AUDUSD','USDCAD'],
                # 'Scandies': ['EURNOK','EURSEK','NOKSEK','USDSEK','USDNOK'],
                # 'CEEMEA' : ['EURPLN','EURCZK','USDILS'],
                # 'Asia EM' : ['USDTWD','USDINR']
            }

maturities_bbg_style = ['2W','1M','3M','6M','1Y']


def crete_bbg_list (fx_master_dict = fx_master_dict):

    implied_real_dict = dict()
    bloomberg_list = list()

    for region in fx_master_dict.keys():

        for fx_pair in fx_master_dict[region]:

            implied_real_dict[fx_pair] = dict()

            for mat in maturities_bbg_style:

                implied_real_dict[fx_pair][mat] = [fx_pair+'V'+mat+' Curncy' , fx_pair+'H'+mat+' Curncy']
                bloomberg_list = bloomberg_list +[fx_pair+'V'+mat+' Curncy' , fx_pair+'H'+mat+' Curncy']


    return implied_real_dict,bloomberg_list



def fx_fetch_implied_bbg(bloomberg_list,StartDate,EndDate):

    blp = BloombergAPI.BLPInterface()
    raw_data = blp.historicalRequest(bloomberg_list, "px_last", StartDate, EndDate)

    return raw_data

def treat_raw_data (raw_data):

    FinalDF = pd.DataFrame()

    IV_percentiles =






if __name__ == "__main__":

    EndDate = date.today()
    StartDate = EndDate - dateutil.relativedelta.relativedelta(months=12)
    implied_real_dict,bloomberg_list = crete_bbg_list (fx_master_dict = fx_master_dict)
    raw_data = fx_fetch_implied_bbg(bloomberg_list,StartDate,EndDate)