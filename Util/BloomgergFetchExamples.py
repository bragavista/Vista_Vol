from Util import BloombergAPI

blp = BloombergAPI.BLPInterface()
StartDate = 20200101
EndDate = 20200201
a = blp.historicalRequest('SPX Index','px_last',StartDate,EndDate)
b = blp.referenceRequest('SPX Index','PX_LAST')
print(a)