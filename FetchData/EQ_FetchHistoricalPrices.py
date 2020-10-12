try:
    from Util import BloombergAPI_new as BloombergAPI
except:
    import Util.BloombergAPI_new as BloombergAPI

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
    # prices = blp.historicalRequest(AssetList, ["PX_LAST"], StartDate, EndDate,adjustmentSplit=True)
    prices = blp.historicalRequest(AssetList, ["PX_LAST"], StartDate, EndDate, CshAdjNormal=CshAdjNormal,adjustmentSplit=True)
    # prices = blp.historicalRequest(AssetList, ["PX_LAST"], StartDate, EndDate)
    blp.close()


    return prices



if __name__ == "__main__":

    StartDate = 20150615
    EndDate = 20201009
    x = ["MCD US Equity"]
    prices = pull_price_history(AssetList=x,StartDate=StartDate,EndDate=EndDate)
    print(prices)