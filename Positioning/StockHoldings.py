try:
    from Util import BloombergAPI_new as BloombergAPI
except:
    import Util.BloombergAPI_new as BloombergAPI
import pandas as pd
import numpy as np
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

        if pace <0:
            liquidation_volume_last = liquidation_volume_last.loc[liquidation_volume_last['position_change_pct'] < pace]
        else:
            liquidation_volume_last = liquidation_volume_last.loc[liquidation_volume_last['position_change_pct'] > pace]

        if ccy_den==reportingccy:
            fx_rate = 1
        else:
            fx_rate = fx_rates[ccy_den+reportingccy+' Curncy']

        liquidation_volume_last['position_'+reportingccy] = round(liquidation_volume_last['Position '] * fx_rate * current_spot_px,0)

        LiquidationStock = LiquidationStock.append(liquidation_volume_last)



    LiquidationStock = LiquidationStock.sort_values(by=['Filing Date  ','position_BRL'],ascending=[False,True])


    return LiquidationStock






if __name__ == "__main__":


    RelatedStockList = ["PETR4 BZ Equity","PETR3 BZ Equity","PBR US Equity","PBR/A US Equity"]
    reportingccy = 'BRL'
    pace = -0.1

    LiquidationStock = do_all_related_stocks (RelatedStockList,'BRL',pace)

    print(LiquidationStock)
    print(RelatedStockList,'remaining value of liquidation',reportingccy,round(LiquidationStock['position_'+reportingccy].sum()/1e9,1),'billion of holders selling at a liquidation pace of ',pace,'of their previous holdings')

