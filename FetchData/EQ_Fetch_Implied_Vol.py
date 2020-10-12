try:
    from Util import BloombergAPI_new as BloombergAPI
except:
    import Util.BloombergAPI_new as BloombergAPI


def Fetch_IV_from_BBG_IVOL_DELTA(AssetList,StartDate,EndDate,Maturity,Delta,Call_Put):

    certainly_valid_dates = ['30d','60d','90d','180d','360d','540d','720d']


    if Call_Put[0].lower()=='p':
        Call_Put_adj='PUT'
    elif Call_Put[0].lower()=='c':
        Call_Put_adj = 'CALL'
    else:
        print('error in Fetch_IV_from_BBG, probably put or call not properly assigned')

    overrides_final = {     "IVOL_MATURITY":"maturity_"+Maturity,
                            "IVOL_DELTA_LEVEL":"delta_lvl_"+Delta,
                            "IVOL_DELTA_PUT_OR_CALL":"IVOL_"+Call_Put_adj                 }

    blp = BloombergAPI.BLPInterface()
    final_iv = blp.historicalRequest(AssetList, ["IVOL_DELTA"], StartDate, EndDate, overrides=overrides_final)
    blp.close()

    return final_iv





if __name__ == "__main__":

    StartDate = 20200618

    EndDate = 20200718

    x = ["SPX Index","IBOV Index","EEM US Equity"]
    # blp = BloombergAPI.BLPInterface()
    # print(blp.historicalRequest("SPX Index", ["IVOL_DELTA"], StartDate, EndDate))
    # print(blp.historicalRequest("SPX Index", ["IVOL_DELTA"], StartDate, EndDate,overrides={"IVOL_MATURITY":"maturity_90d"}))
    # print(blp.historicalRequest("SPX Index", ["IVOL_DELTA"], StartDate, EndDate,overrides={"IVOL_MATURITY":"maturity_30d",
    #                                                                                        "IVOL_DELTA_LEVEL":'delta_lvl_50',
    #                                                                                        "IVOL_DELTA_PUT_OR_CALL":"IVOL_PUT",
    #                                                                                        }))
    # blp.close()

    print(Fetch_IV_from_BBG_IVOL_DELTA(AssetList=x, StartDate=StartDate, EndDate=EndDate, Maturity='30d',Delta= '25', Call_Put='call'))



