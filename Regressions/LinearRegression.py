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
        estimate_beta = []
        estimate_alpha = []
        for i in range(window, x.index.size+1):
            # print (i)
            X_slice = X.values[i-window:i,:] # always index in np as opposed to pandas, much faster
            y_slice = y.values[i-window:i]
            coeff = np.dot(np.dot(np.linalg.inv(np.dot(X_slice.T, X_slice)), X_slice.T), y_slice)
            est = coeff[0] * x.values[window-1] + coeff[1]
            estimate_data.append(est)
            estimate_beta.append(coeff[0])
            estimate_alpha.append(coeff[1])
    # === Assemble ========================================================
        estimate = pd.Series(data=estimate_data, index=x.index[window-1:]).to_frame()
        estimate.columns = ['model']
        estimate_beta = pd.Series(data=estimate_beta, index=x.index[window - 1:]).to_frame()
        estimate_beta.columns = ['beta']

        estimate_alpha = pd.Series(data=estimate_alpha, index=x.index[window - 1:]).to_frame()
        estimate_alpha.columns = ['alpha']
        estimate = pd.concat([estimate,estimate_beta,estimate_alpha],axis=1,sort=True)

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


regressions_dict = {}

for item in RegressionDict_bbg.keys():
    print(item)

    xx = AllPrices[RegressionDict_bbg[item]['x']]
    x_name = RegressionDict_bbg[item]['x']
    yy = AllPrices[RegressionDict_bbg[item]['y']]
    y_name = RegressionDict_bbg[item]['y']

    plt.scatter(xx,yy)

    yy_est = rolling_regression(yy, xx, window=30)
    yy_est.columns = [y_name +'-' +name for name in yy_est.columns]

    df_model = pd.concat([yy_est,yy],sort=True,axis=1)

    df_model['residual'] = df_model[y_name].values - df_model[y_name+'-model']

    df_model[x_name] = xx

    regressions_dict[item] = df_model





