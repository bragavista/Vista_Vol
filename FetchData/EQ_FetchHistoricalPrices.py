try:
    from Util import BloombergAPI_new as BloombergAPI
except:
    import Util.BloombergAPI_new as BloombergAPI
import pandas as pd
def pull_price_history (AssetList,StartDate,EndDate, CshAdjNormal=False):

    #
    # overrides_final = {     "IVOL_MATURITY":"maturity_"+Maturity,
    #                         "IVOL_DELTA_LEVEL":"delta_lvl_"+Delta,
    #                         "IVOL_DELTA_PUT_OR_CALL":"IVOL_"+Call_Put_adj                 }
    #

    defaults1 = {
                # 'periodicityAdjustment': 'CALENDAR',
                # 'periodicitySelection': 'DAILY',
                # 'nonTradingDayFillOption': 'NON_TRADING_WEEKDAYS',
                # 'adjustmentNormal': False,
                # 'adjustmentAbnormal': False,
                # 'adjustmentSplit': True,
                # 'adjustmentFollowDPDF': False
                }

    blp = BloombergAPI.BLPInterface()

    prices = blp.historicalRequest(AssetList, ["PX_LAST"], StartDate, EndDate, CshAdjNormal=CshAdjNormal,adjustmentSplit=True)
    prices.index = prices.index.date

    blp.close()


    return prices


def pull_multiple_fields_history (AssetList,StartDate,EndDate, fields_list,CshAdjNormal=False):

    #
    # overrides_final = {     "IVOL_MATURITY":"maturity_"+Maturity,
    #                         "IVOL_DELTA_LEVEL":"delta_lvl_"+Delta,
    #                         "IVOL_DELTA_PUT_OR_CALL":"IVOL_"+Call_Put_adj                 }
    #

    defaults1 = {
                # 'periodicityAdjustment': 'CALENDAR',
                # 'periodicitySelection': 'DAILY',
                # 'nonTradingDayFillOption': 'NON_TRADING_WEEKDAYS',
                # 'adjustmentNormal': False,
                # 'adjustmentAbnormal': False,
                # 'adjustmentSplit': True,
                # 'adjustmentFollowDPDF': False
                }

    blp = BloombergAPI.BLPInterface()

    prices = blp.historicalRequest(AssetList, fields_list, StartDate, EndDate, CshAdjNormal=CshAdjNormal,adjustmentSplit=True)
    prices.index = prices.index.date

    blp.close()


    return prices






if __name__ == "__main__":

    StartDate = 20150130
    EndDate = 20201113
    x = ["VISTMUL BZ Equity",'BZACCETP Index']
    prices = pull_price_history(AssetList=x,StartDate=StartDate,EndDate=EndDate)
    prices.columns = ['PX_LAST']
    # prices_daily = prices.pct_change()
    # maxday = prices_daily.max()[0]
    # prices_daily.loc[prices_daily['PX_LAST']==maxday]
    print(prices)
