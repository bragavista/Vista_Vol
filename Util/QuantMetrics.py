import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.colors as mcolors


def corr_matrix_from_prices (PricesDataframe):

    returns = PricesDataframe.pct_change().fillna(0)

    corr_matrix = returns.corr(method='pearson')

    return corr_matrix


def corr_matrix_masking (corr_matrix):
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

    sns.heatmap(corr_matrix, annot=True, mask=matrix,cmap=cmap,linewidths=3, linecolor='white',cbar=False)

    return


