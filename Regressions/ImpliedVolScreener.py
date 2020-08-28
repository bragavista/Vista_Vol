import BloombergAPI
import datetime
from dateutil.relativedelta import relativedelta

#date start and end creation
MonthsBackTestPeriod = 12
EndDateObj = datetime.now().date()
EndDate = EndDateObj.strftime('%Y%m%d')
RiskMetricPeriod = relativedelta(months=-MonthsBackTestPeriod)
StartDateObj = EndDateObj + RiskMetricPeriod
StartDAte = StartDateObj.strftime('%Y%m%d')

List_of_FX_Pairs = ['USDBRL','USDMXN','EURMXN','USDCOP','USDCLP']