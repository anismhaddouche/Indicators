#Importation des librairies
from IPython.display import display,HTML
import datetime
import umap
#import umap.plot
from sklearn.cluster import DBSCAN
import warnings
#import hdbscan
import seaborn as sns
from sklearn_extra.cluster import KMedoids
from mpl_toolkits.mplot3d import Axes3D
from sklearn.metrics import silhouette_score
from sklearn.cluster import KMeans
from sklearn import decomposition
import numpy as np
import pandas as pd
import sklearn
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
# Pour les biplot
from bioinfokit.visuz import cluster
from IPython import display
import scipy.cluster.hierarchy as shc
from sklearn.cluster import AgglomerativeClustering
from sklearn.preprocessing import PowerTransformer
from scipy import stats
from sklearn.preprocessing import QuantileTransformer
pt = PowerTransformer()
qt = QuantileTransformer(output_distribution='normal')

import matplotlib.pyplot as plt3D
pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)
pd.set_option('display.max_colwidth', 100)
warnings.filterwarnings('ignore')

# Display two data frame usage diplay(display_side_by_side(df1,df2,['titre1','titre2']))


def display_side_by_side(dfs: list, captions: list, tablespacing=5):
    """Display tables side by side to save vertical space
    Input:
        dfs: list of pandas.DataFrame
        captions: list of table captions
    """
    output = ""
    for (caption, df) in zip(captions, dfs):
        output += df.style.set_table_attributes(
            "style='display:inline'").set_caption(caption)._repr_html_()
        output += tablespacing * "\xa0"
    return HTML(output)


def ArbreDecision(df, NameBalContr, NameCoEcri, SeuilBalContr=(0, .33, .66, 1), SeuilCoEcri=(0, .33, .66, 1), clusters=["00", "01", "02", "10", "11", "12", "20", "21", "22"]):
    '''df : notre data frame
     NameBalContr : le nom de la variable balance_contribution
     NameCoEcri : le nom de la variable co_écriture
     SeuilBalContr : les seuils décisions  de col1 ex : (0,.33,.66, .1)
     SeuilCoEcri : les seuils décisions  de col1
     Tags : 0 -> Faible, 1-> Moyen, 2 -> Fort
     clusters : 01 Faible balance_contribution et co_écriture moyenne '''
    for ligne in range(np.shape(df)[0]):
       BalContr, CoEcri = df[NameBalContr].iloc[ligne], df[NameCoEcri].iloc[ligne]

# balance_contribution faible
       if SeuilBalContr[0] <= BalContr <= SeuilBalContr[1]:
           if SeuilCoEcri[0] <= CoEcri <= SeuilCoEcri[1]:
               df["labels_ArbreDecision"].iloc[ligne] = 0

           elif SeuilCoEcri[1] < CoEcri <= SeuilCoEcri[2]:
               df["labels_ArbreDecision"].iloc[ligne] = 1

           elif SeuilCoEcri[2] < CoEcri <= SeuilCoEcri[3]:
               df["labels_ArbreDecision"].iloc[ligne] = 2


# balance_contribution moyenne
       elif SeuilBalContr[1] < BalContr <= SeuilBalContr[2]:
           if SeuilCoEcri[0] <= CoEcri <= SeuilCoEcri[1]:
                df["labels_ArbreDecision"].iloc[ligne] = 3

           elif SeuilCoEcri[1] < CoEcri <= SeuilCoEcri[2]:
               df["labels_ArbreDecision"].iloc[ligne] = 4

           elif SeuilCoEcri[2] < CoEcri <= SeuilCoEcri[3]:
               df["labels_ArbreDecision"].iloc[ligne] = 5


# balance_contribution forte
       elif SeuilBalContr[2] < BalContr <= SeuilBalContr[3]:
           if SeuilCoEcri[0] <= CoEcri <= SeuilCoEcri[1]:
                df["labels_ArbreDecision"].iloc[ligne] = 6

           elif SeuilCoEcri[1] < CoEcri <= SeuilCoEcri[2]:
               df["labels_ArbreDecision"].iloc[ligne] = 7

           elif SeuilCoEcri[2] < CoEcri <= SeuilCoEcri[3]:
               df["labels_ArbreDecision"].iloc[ligne] = 8

    df.labels_ArbreDecision = df.labels_ArbreDecision.astype(int)
