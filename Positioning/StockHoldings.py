import sys
sys.path.append('C:\\Users\\ArthurBraga\\PycharmProjects\\')
sys.path.append('C:\\Users\\ArthurBraga\\PycharmProjects\\Vista\\')
sys.path.append('C:\\Users\\ArthurBraga\\PycharmProjects\\Vista\\Util\\')

try:
    from Util import BloombergAPI_new as BloombergAPI
    from Util import random_functions as random_functions
    from Util import EmailSender as EmailSender

except:
    import Util.BloombergAPI_new as BloombergAPI
    import Util.random_functions as random_functions
    import Util.EmailSender as EmailSender


import pandas as pd
import numpy as np
from datetime import date

pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)
#*the historic change in ownership by large owner is not in bbg now

def fetch_holders_info(StockTicker):

    blp = BloombergAPI.BLPInterface()

    all_holders_public_filiings = blp.bulkRequest(StockTicker,"ALL_HOLDERS_PUBLIC_FILINGS")


    blp.close()

    return all_holders_public_filiings

def sort_by_position_change(all_holders_public_filiings,threshold_position_left_pct=0.10, sell_or_buy='sell'):


    big_holders = all_holders_public_filiings.loc[all_holders_public_filiings['Percent Outstanding']>=threshold_position_left_pct]

    if sell_or_buy=='sell':

        active_big_holders = big_holders.loc[big_holders['Position Change  ']<0]
    elif sell_or_buy=='buy':
        active_big_holders = big_holders.loc[big_holders['Position Change  ']>0]

    else:
        print('mistake')
        return 'mistake'


    active_big_holders['position_change_pct'] = active_big_holders['Position Change  '] / abs((active_big_holders['Position Change  '] - active_big_holders['Position ']))

    active_big_holders = active_big_holders.sort_values(by=['position_change_pct','Filing Date  '],ascending=True)




    return active_big_holders




def do_all_related_stocks (RelatedStockList,reportingccy, pace):


    blp = BloombergAPI.BLPInterface()
    prices_map = blp.referenceRequest(RelatedStockList, "PX_LAST")
    ccy_map =     blp.referenceRequest(RelatedStockList, "CRNCY")
    unique_ccy_list = list(np.unique(ccy_map.values))
    unique_ccy_list.remove(reportingccy)
    fx_rates_list = [ccy+reportingccy+' Curncy' for ccy in unique_ccy_list]
    fx_rates = blp.referenceRequest(fx_rates_list, "PX_LAST")

    blp.close()

    LiquidationStock = pd.DataFrame()

    for StockTicker in RelatedStockList:

        current_spot_px = prices_map[StockTicker]

        ccy_den = ccy_map[StockTicker]

        all_holders_public_filiings = fetch_holders_info(StockTicker)

        active_big_holders = sort_by_position_change(all_holders_public_filiings, threshold_position_left_pct=0.10, sell_or_buy='sell')

        liquidation_volume_last = active_big_holders[['Filing Date  ','Holder Name ','Percent Outstanding','Position ', 'Position Change  ', 'position_change_pct']]

        liquidation_volume_last['StockTicker'] = StockTicker.replace(' Equity','')

        liquidation_volume_last['reportingccy'] = reportingccy

        if pace <0:
            liquidation_volume_last = liquidation_volume_last.loc[liquidation_volume_last['position_change_pct'] < pace]
        else:
            liquidation_volume_last = liquidation_volume_last.loc[liquidation_volume_last['position_change_pct'] > pace]

        if ccy_den==reportingccy:
            fx_rate = 1
        else:
            fx_rate = fx_rates[ccy_den+reportingccy+' Curncy']

        liquidation_volume_last['volume_in_reportingccy_mm'] = -round((liquidation_volume_last['Position '] * fx_rate * current_spot_px)/1e6,0)

        LiquidationStock = LiquidationStock.append(liquidation_volume_last)



    LiquidationStock = LiquidationStock.sort_values(by=['Filing Date  ','volume_in_reportingccy_mm'],ascending=[False,False])


    return LiquidationStock


def capture_top_holdings_fund (FundName='TEMPOCA BZ Equity',n=10):

    blp = BloombergAPI.BLPInterface()

    top_holdings = blp.bulkRequest(FundName, "TOP_MUTUAL_FUND_HOLDINGS")

    blp.close()


    return top_holdings


def do_all_stocks (target_stock_dict,pace=-0.1):

    all_target_stocks = pd.DataFrame()
    all_selling_stock = pd.DataFrame()

    for stock in target_stock_dict.keys():

        reportingccy = target_stock_dict[stock]['reportingccy']
        RelatedStockList = target_stock_dict[stock]['RelatedStockList']
        LiquidationStock = do_all_related_stocks(RelatedStockList,reportingccy, pace)
        LiquidationStock['StockGroup'] = stock

        Potential_Selling_Stock = LiquidationStock['volume_in_reportingccy_mm'].sum()

        total_aux = pd.DataFrame(data=[Potential_Selling_Stock],index=[stock],columns=['PotentialLiquidation_' + reportingccy + '_mm'])

        all_target_stocks = all_target_stocks.append([LiquidationStock,total_aux])
        # all_target_stocks = all_target_stocks.fillna('')

        all_selling_stock = all_selling_stock.append(total_aux)


    # print(RelatedStockList,'remaining value of liquidation',,LiquidationStock['position_'+reportingccy+'_mm'].sum(),'mm of holders selling at a liquidation pace of ',pace,'of their previous holdings')

    return  all_target_stocks,all_selling_stock



def recent_activity_calc(all_target_stocks,cutdate):

    recent_activity = all_target_stocks.loc[all_target_stocks['Filing Date  '] >= cutdate]


    recent_activity = recent_activity[['Filing Date  ','StockGroup','StockTicker','volume_in_reportingccy_mm','Holder Name ','Position ','Position Change  ','position_change_pct','reportingccy']]

    return recent_activity



if __name__ == "__main__":

    cutdate = random_functions.prev_weekday(date.today())

    RelatedStockList = ["PETR4 BZ Equity","PETR3 BZ Equity","PBR US Equity","PBR/A US Equity"]
    reportingccy = 'BRL'
    pace = -0.1

    target_stock_dict = {
                                'PETROBRAS' :  { 'reportingccy': 'BRL','RelatedStockList': ["PETR4 BZ Equity","PETR3 BZ Equity","PBR US Equity","PBR/A US Equity"]} ,
                                'VALE' :       {'reportingccy':'BRL','RelatedStockList':["VALE3 BZ Equity","VALE5 BZ Equity",'VALE US Equity']} ,
                                'LREN' :  { 'reportingccy': 'BRL','RelatedStockList': ['LREN3 BZ Equity','LRENY US Equity']},
                                'NATURA' :  { 'reportingccy': 'BRL','RelatedStockList': ['NTCO3 BZ Equity', 'NTCO US Equity']},
                                'ITAU':     { 'reportingccy': 'BRL','RelatedStockList': ['ITUB3 BZ Equity', 'ITUB4 BZ Equity','ITUB US Equity']}

                    }

    all_target_stocks,all_selling_stock = do_all_stocks(target_stock_dict, pace=-0.1)

    recent_activity = recent_activity_calc(all_target_stocks, cutdate)




    print(recent_activity)
    print(all_selling_stock)
    print(all_target_stocks)


    #creating html for email
    html_string1 = 'Most Recent Position Liquidation Reported for ' + str(list(target_stock_dict.keys())) +  recent_activity.to_html() + '<br>'+ '<br>'

    html_string2 = 'Full Liquidation Volume for Holders who have been cutting at least ' + str(100*pace) + '% of position'   + all_selling_stock.to_html() + '<br>'+ '<br>'

    html_string3 = 'Liquidation Volume per Holder who have been cutting at least '+ str(100*pace) + '% of position' + all_target_stocks.to_html() + '<br>'+ '<br>'

    html_string = html_string1 + html_string2 + html_string3

    subject = str(cutdate) + ' - Large Equity Liquidations - ' + str(list(target_stock_dict.keys()))
    mail_to = 'analise@vistacapital.com.br'
    # mail_to = 'abraga@vistacapital.com.br'


    EmailSender.send_email_simple (mail_to=mail_to,subject=subject,bodymsg='hi',html_body=html_string,attachment=False)




    # print(RelatedStockList,'remaining value of liquidation',reportingccy,LiquidationStock['position_'+reportingccy+'_mm'].sum(),'mm of holders selling at a liquidation pace of ',pace,'of their previous holdings')

