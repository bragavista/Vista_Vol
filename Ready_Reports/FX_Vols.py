# from importlib import import_module
# BloombergAPI = import_module("Util.BloombergAPI")
import time
print('starting things here')
import os
import sys
sys.path.append('C:\\Users\\ArthurBraga\\PycharmProjects\\')
sys.path.append('C:\\Users\\ArthurBraga\\PycharmProjects\\Vista\\')
sys.path.append('C:\\Users\\ArthurBraga\\PycharmProjects\\Vista\\Util\\')

# import Util.BloombergAPI_new as BloombergAPI
# import Util.QuantMetrics as QuantMetrics
# import Util.EmailSender as EmailSender
try:
    import Util
    from Util import BloombergAPI_new as BloombergAPI
    from Util import QuantMetrics as QuantMetrics
    from Util import EmailSender as EmailSender
    print('try worked')

except:
    import Util.BloombergAPI_new as BloombergAPI
    import Util.QuantMetrics as QuantMetrics
    import Util.EmailSender as EmailSender

time.sleep(5)


import pandas as pd
import seaborn as sns
from datetime import date
import dateutil.relativedelta

pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

heatmap_green_red = sns.diverging_palette(160, 10, n=7,as_cmap=True)
# sns.palplot(sns.diverging_palette(160, 10, n=7))



maturities_bbg_style = ['1M','3M','6M','1Y']



def crete_bbg_list (fx_master_dict):

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



if __name__ == "__main__":

    fx_master_dict = QuantMetrics.fx_master_dict
    last_n_months = 12
    print('hello, calculating FX iv and iv-rv data now')
    EndDate = date.today()
    StartDate = EndDate - dateutil.relativedelta.relativedelta(months=last_n_months)
    implied_dict,real_dict,bloomberg_list = crete_bbg_list (fx_master_dict = fx_master_dict)
    raw_data = fx_fetch_implied_bbg(bloomberg_list,StartDate,EndDate)

    #creating DFs
    Implied_Percentiles = QuantMetrics.treat_raw_data_iv_pctle(implied_dict, raw_data)
    print(Implied_Percentiles)

    Implied_minus_Realized_Percentiles = QuantMetrics.treat_raw_data_iv_minus_rv_pctle(implied_dict, real_dict, raw_data)
    print(Implied_minus_Realized_Percentiles)

    #formatting dfs
    subset_heatmap = list()
    for column in Implied_minus_Realized_Percentiles.columns:
        if "pctle" in column:
            subset_heatmap.append(column)

    pre_render = Implied_minus_Realized_Percentiles.style.background_gradient(cmap=heatmap_green_red,subset=subset_heatmap).set_precision(1).set_properties(**{'text-align': 'center'})
    Implied_minus_Realized_Percentiles_final = pre_render.render()

    #formatting another DF
    subset_heatmap = list()
    for column in Implied_Percentiles.columns:
        if "pctle" in column:
            subset_heatmap.append(column)

    pre_render2 = Implied_Percentiles.style.background_gradient(cmap=heatmap_green_red,subset=subset_heatmap).set_precision(1).set_properties(**{'text-align': 'center'})
    Implied_Percentiles_final = pre_render2.render()



    #creating html for email
    html_string = str(last_n_months) + ' months of data - Vol buying candidates in green, Vol selling candidates in red' + '<br>'+'<br>'+ Implied_Percentiles_final + '<br>'+Implied_minus_Realized_Percentiles_final
    subject = 'FX Vol Baseline for ' + str(EndDate)
    mail_to = 'mesa@vistacapital.com.br'
    # mail_to = 'abraga@vistacapital.com.br'

    EmailSender.send_email_simple (mail_to=mail_to,subject=subject,bodymsg='hi',html_body=html_string,attachment=False)


