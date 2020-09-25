import pandas as pd
from Util import QuantMetrics, BloombergAPI_new
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np


pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)


FundList = [    "VISTMUL BZ Equity",
                "IFMMIFMM Index",
                "STHFIC BZ Equity",
                "KAPKFFF BZ Equity",
                "SPXNIMF BZ Equity",
                "BBMFIC BZ Equity",
                "ABVRTFF BZ Equity",
                "DARTFIC BZ Equity",
                "ADVEII BZ Equity",
                "CSH2086 BZ Equity",
                "ADM1MCR BZ Equity",
                "BRPLABF BZ Equity",
                "VNLMADV BZ Equity"
             ]

FundNames = {
                "VISTMUL BZ Equity": "VISTA MULTI",
                "IFMMIFMM Index" : "BTG HF Index",
                "STHFIC BZ Equity":  "ibiuna hedge sth",
                "KAPKFFF BZ Equity": "kapitalo kappa",
                "SPXNIMF BZ Equity": "spx nimitz",
                "BBMFIC BZ Equity":  "bahia marau",
                "ABVRTFF BZ Equity": "absolute vertex",
                "DARTFIC BZ Equity": "garde d'artagnan",
                "ADVEII BZ Equity":  "canvas enduro",
                "MCRCHRN BZ Equity": "kinea chronos",
                "CSH2086 BZ Equity": "legacy capital",
                "ADM1MCR BZ Equity": "adam macro",
                "BRPLABF BZ Equity": "occam retorno abs",
                "VNLMADV BZ Equity": "vinland macro"

}

start_date   =   '20190101'
end_date     =   '20200101'

blp = BloombergAPI_new.BLPInterface()

FundsRawPrices = blp.historicalRequest(FundList,'px_last',start_date,end_date)

corr_matrix = QuantMetrics.corr_matrix_from_prices(PricesDataframe=FundsRawPrices)

cdict = {'red': ((0.0, 0.0, 0.0),
                 (0.5, 0.0, 0.0),
                 (1.0, 1.0, 1.0)),
         'blue': ((0.0, 0.0, 0.0),
                  (1.0, 0.0, 0.0)),
         'green': ((0.0, 0.0, 1.0),
                   (0.5, 0.0, 0.0),
                   (1.0, 0.0, 0.0))}
cmap = mcolors.LinearSegmentedColormap(
    'my_colormap', cdict, 100)
# cmap = sns.palplot(sns.diverging_palette(10, 220, sep=80, n=7))
matrix = np.triu(corr_matrix)
ax = plt.axes()
sns.heatmap(corr_matrix.round(2), annot=True, mask=matrix, cmap=cmap, linewidths=3, linecolor='white', cbar=False,ax = ax)
ax.set_title('Daily correlation from ' + start_date + ' to ' + end_date,fontsize=20)
plt.show()


# QuantMetrics.corr_matrix_masking(corr_matrix)


