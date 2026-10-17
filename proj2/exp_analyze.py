############################################################
### Authors: David Navrátil, Matej Melchiory
### Date: 17.10.2026
### Description: Performs exploratory data analysis (EDA) on the dataset, including statistical summaries, data types, missing values, and attribute distributions.
############################################################

from pathlib import Path

import numpy
import pandas
import matplotlib.pyplot
import seaborn as sns
import sklearn

# Paths setup and importing dataset from data.tsv
DATA_PATH = Path("data.tsv")
OUTPUT_DIR = Path("vystupy")

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

TOP_VALUES_COUNT = 10
MAX_VALUES_IN_TERMINAL = 30

sns.set_theme(style="whitegrid")

if not DATA_PATH.exists():
    raise FileNotFoundError(f"Soubor {DATA_PATH} nebyl nalezen. ")

df = pandas.read_csv(DATA_PATH, sep="\t")

df.columns = df.columns.astype(str).str.strip()

if df.columns.duplicated().any():
    raise ValueError("Dataset obsahuje duplicitní názvy sloupců. ")

