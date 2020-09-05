import BloombergAPI_new
import pandas as pd
from Util import QuantMetrics
import seaborn as sns
import matplotlib.pyplot as plt

pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)


FundList = [    "VISTMUL BZ Equity",
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

start_date   =   '20150101'
end_date     =   '20200903'

blp = BloombergAPI_new.BLPInterface()

FundsRawPrices = blp.historicalRequest(FundList,'px_last',start_date,end_date)

corr_matrix = QuantMetrics.corr_matrix_from_prices(PricesDataframe=FundsRawPrices)

sns.heatmap(CorrMatrix,annot=True)
plt.show()


