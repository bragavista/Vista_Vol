from importlib import reload
from pathlib import Path
import os
import sys
import time
from glob import glob

#os.chdir(Path(__file__).parent) # apenas para .py
sys.path.insert(0,'..') # caminho pro parent dir

# DFs + Matematica + Tempo
import numpy as np
import pandas as pd
import scipy.linalg as la
import datetime as dt
import pyodbc as db

# Acesso a Bloomberg
from xbbg import blp
import pdblp


def get_sql():
    # login e senha do sql

    conn = db.connect(r'DRIVER={SQL SERVER};SERVER=192.168.35.254;Database=Vista-DB001;UID=L3\abraga;PWD=Provence123!!')
    # conn = db.connect(r'DRIVER={SQL SERVER};SERVER=192.168.35.253;Database=Vista-DB001;Trusted_Connection=yes;')

    query = """

    SELECT *

    FROM [Vista-DB001].[dbo].[Gerencial_Calculo]

    WHERE [Fundo Gerencial] = 'VISTA MULTIESTRATEGIA FIC FIM'

    """

    base = pd.read_sql(query, conn)
    return base

print (get_sql())