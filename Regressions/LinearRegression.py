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
import pandas as pd
import matplotlib.pyplot as plt



def rolling_regression(y, x, window=60):
    """
    y and x must be pandas.Series
    """
# === Clean-up ============================================================
    x = x.dropna()
    y = y.dropna()
# === Trim acc to shortest ================================================
    if x.index.size > y.index.size:
        x = x[y.index]
    else:
        y = y[x.index]
# === Verify enough space =================================================
    if x.index.size < window:
        return None
    else:
    # === Add a constant if needed ========================================
        X = x.to_frame()
        X['c'] = 1
    # === Loop... this can be improved ====================================
        estimate_data = []
        for i in range(window, x.index.size+1):
            # print (i)
            X_slice = X.values[i-window:i,:] # always index in np as opposed to pandas, much faster
            y_slice = y.values[i-window:i]
            coeff = np.dot(np.dot(np.linalg.inv(np.dot(X_slice.T, X_slice)), X_slice.T), y_slice)
            est = coeff[0] * x.values[window-1] + coeff[1]
            estimate_data.append(est)
    # === Assemble ========================================================
        estimate = pd.Series(data=estimate_data, index=x.index[window-1:])
        return estimate


StartDate = 20200901
EndDate = 20201118


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
AllPrices = EQ_FetchHistoricalPrices.pull_price_history(all_assets,StartDate=StartDate,EndDate=EndDate)
AllPrices.columns = [element[0] for element in AllPrices.columns]


for item in RegressionDict_bbg.keys():
    print(item)

    xx = AllPrices[RegressionDict_bbg[item]['x']]
    yy = AllPrices[RegressionDict_bbg[item]['y']]

    plt.scatter(xx,yy)

    yy_est = rolling_regression(yy, xx, window=30).to_frame()
    yy_est.columns = ['model']


    df_model = pd.concat([yy_est,yy],sort=True,axis=1)
    df_model['residual'] = df_model['VIX Index'].values - df_model.model





