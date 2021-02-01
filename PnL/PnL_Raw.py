import pandas as pd

pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

raw_data = pd.read_csv("C:\\Users\\ArthurBraga\\PycharmProjects\Vista\\PnL\\ResultadoVarSwap RAW.csv")
raw_data['Date'] = raw_data['Date'].astype('datetime64[ns]')
raw_data = raw_data.sort_values(by=['Date'],ascending=True)

removing_long_spx = raw_data.loc[raw_data['Vega Notional']<=0]

removing_short_ndx = removing_long_spx.loc[removing_long_spx['Product'].str.contains('SPX')]

daily_global_pnl = removing_short_ndx[['Date','Financial PnL']].groupby('Date').sum()

daily_global_pnl_sorteddate = daily_global_pnl.sort_values(by=['Date'],ascending=True)

daily_global_cumsum = daily_global_pnl_sorteddate.cumsum()


daily_global_cumsum.plot()