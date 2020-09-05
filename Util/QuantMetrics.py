import pandas as pd
import numpy as np


def corr_matrix_from_prices (PricesDataframe):

    returns = PricesDataframe.pct_change().fillna(0)

    corr_matrix = returns.corr(method='pearson')

    return corr_matrix





