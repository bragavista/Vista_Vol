from FetchData import data
import datetime as dt
import pandas as pd
import numpy as np

conn = data.bbg_conn()
conn.start()
data_wdw = 365*11
end_dt = dt.date(2020,8,11)
start_dt = (end_dt - dt.timedelta(data_wdw))
eq_undl = data.equity(['SPX Index','NKY Index'])

eq_iv_live_25 = eq_undl.ivol(252,'delta',25,start_dt,end_dt,connection=conn,p_or_c='put',price_choice='mid',source='live')
eq_iv_live_10 = eq_undl.ivol(252,'delta',10,start_dt,end_dt,connection=conn,p_or_c='put',price_choice='mid',source='live')
eq_iv_live_50 = eq_undl.ivol(252,'delta',50,start_dt,end_dt,connection=conn,p_or_c='put',price_choice='mid',source='live')


print (eq_iv_live_10)


conn.stop()