from Util import BloombergAPI_new as BloombergAPI

StartDate = 20200618
EndDate = 20200718
x = "IBOV Index"

blp = BloombergAPI.BLPInterface()
print(blp.historicalRequest("SPX Index", ["IVOL_DELTA"], StartDate, EndDate))
print(blp.historicalRequest("SPX Index", ["IVOL_DELTA"], StartDate, EndDate,overrides={"IVOL_MATURITY":"maturity_90d"}))
print(blp.historicalRequest("SPX Index", ["IVOL_DELTA"], StartDate, EndDate,overrides={"IVOL_MATURITY":"maturity_30d"}))
blp.close()
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
