try:
    from Util import BloombergAPI_new as BloombergAPI
except:
    import Util.BloombergAPI_new as BloombergAPI
import pandas as pd
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





if __name__ == "__main__":

    StockTicker = "PETR3 BZ Equity"

    all_holders_public_filiings = fetch_holders_info(StockTicker)

    active_big_holders = sort_by_position_change(all_holders_public_filiings, threshold_position_left_pct=0.10, sell_or_buy='sell')

    liquidation_volume_last = active_big_holders[['Filing Date  ','Holder Name ','Percent Outstanding','Position ', 'Position Change  ', 'position_change_pct']]

    liquidation_pace = 0.1
    liquidation_volume_last = liquidation_volume_last.loc[liquidation_volume_last['position_change_pct']< -liquidation_pace]

    print(liquidation_volume_last)
    print(StockTicker,'remaining stock of liquidation',round(liquidation_volume_last['Position '].sum()/1e6,1),'million shares of holders selling at a liquidation pace of ',-liquidation_pace,'of their previous holdings')

