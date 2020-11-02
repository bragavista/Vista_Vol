try:
    import Util
    from Util import BloombergAPI_new as BloombergAPI
    from Util import QuantMetrics as QuantMetrics
    from Util import EmailSender as EmailSender
    from FetchData import EQ_FetchHistoricalPrices
    print('try worked')

except:
    import Util.BloombergAPI_new as BloombergAPI
    import Util.QuantMetrics as QuantMetrics
    import Util.EmailSender as EmailSender
    import FetchData.EQ_FetchHistoricalPrices as EQ_FetchHistoricalPrices

import numpy as np
StartDate = 20200618
EndDate = 20200718
y = "VIX Index"
x = "SPX Index"

RegressionDict_bbg = {  'vix_spx' :
                                {'y' : "VIX Index", 'x' : "SPX Index"},
                    'credit_hy_SPX':
                                {'y' : "CDX HY CDSI GEN 5Y PRC Index", 'x' : "SPX Index"},
                    'credit_ig_SPX':
                                {'y' : "CDX IG CDSI GEN 5Y SPRD Index", 'x' : "SPX Index"},
                    'vix_credit_hy':
                                {'y' : "VIX Index", 'x' : "CDX HY CDSI GEN 5Y PRC Index"}
                    }

all_assets = list()
for item in RegressionDict_bbg.keys():
    print(item)
    for subitem in RegressionDict_bbg[item]:
        all_assets.append(RegressionDict_bbg[item][subitem])
all_assets = list(np.unique(all_assets))

all_history = EQ_FetchHistoricalPrices.pull_price_history (all_assets,StartDate,EndDate, CshAdjNormal=False)













# print(y)
#
#
# ovrds_=[("IVOL_DELTA_LEVEL","DELTA_LVL_25"),("IVOL_DELTA_PUT_OR_CALL","IVOL_PUT"),("IVOL_MATURITY","MATURITY_90D")]
# ovrds_=[("IVOL_MATURITY","maturity_90d")]
#
#
# y = blp.historicalRequest("SPX Index", "IVOL_DELTA", StartDate, EndDate,[("IVOL_MATURITY","maturity_90d")])
# print(y)
# blp.close()
#
# bbg_overds = [('ivol_delta_put_or_call', 'ivol_' + ('put' if p_or_c == 'p' else 'call')),
#               ('ivol_maturity', 'maturity' + str(tenor_map[tenor]) + 'd'),
#               ('ivol_delta_level', 'delta_lvl' + str(strike))]
#
#
#
# y = blp.historicalRequest('SPX Index', 'IVOL_DELTA', StartDate, EndDate, IVOL_DELTA_PUT_OR_CALL='IVOL_PUT',
#                           IVOL_MATURITY='maturity_30D', IVOL_DELTA_LEVEL='delta_lvl_50')
# print(y)
#
# # defaults1 = {'startDate': StartDate,
# #             'endDate': EndDate,
# # }
# #
# # # Keyword arguments are added to the request, allowing you to perform advanced queries.
# # print(blp.historicalRequest('TD CN Equity', 'PCT_CHG_INSIDER_HOLDINGS', '20141231', '20150131',
# #                             periodicitySelection='WEEKLY'))
# #
# # print(blp.historicalRequest('SPX Index', 'IVOL_DELTA', '20200515', '20200818','IVOL'))
# #
# # # y = blp.historicalRequest('SPX Index','IVOL_DELTA',defaults1)
