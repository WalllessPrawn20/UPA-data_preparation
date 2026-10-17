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
DATA_PATH = Path("proj2/data.tsv")
OUTPUT_DIR = Path("proj2/vystupy")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
REPORT_PATH = OUTPUT_DIR / "analyza.txt"

TOP_VALUES_COUNT = 10
MAX_VALUES_IN_TERMINAL = 30

sns.set_theme(style="whitegrid")

if not DATA_PATH.exists():
    raise FileNotFoundError(f"Soubor {DATA_PATH} nebyl nalezen. ")

df = pandas.read_csv(DATA_PATH, sep="\t", header=None)

df.columns = df.columns.astype(str).str.strip()

if df.columns.duplicated().any():
    raise ValueError("Dataset obsahuje duplicitní názvy sloupců. ")

# Functions for report
def write_section(report, title):
    report.write("\n")
    report.write("=" * 80 + "\n")
    report.write(f"{title}\n")
    report.write("=" * 80 + "\n\n")

def write_subsection(report, title):
    report.write("\n")
    report.write("-" * 80 + "\n")
    report.write(f"{title}\n")
    report.write("-" * 80 + "\n")

def write_field(report, label, value, width=38):
    report.write(f"{label:<{width}} {value}\n")

def format_value(value):
    if pandas.isna(value):
        return "<CHYBĚJÍCÍ HODNOTA>"

    if isinstance(value, numpy.generic):
        value = value.item()

    return str(value)

def write_table(report, headers, rows):
    if not headers:
        return

    formatted_rows = [[format_value(value) for value in row] for row in rows]

    widths = []

    for index, header in enumerate(headers):
        max_width = len(str(header))

        for row in formatted_rows:
            max_width = max(max_width, len(row[index]))

        widths.append(max_width)

    header_line = " | ".join(
        str(header).ljust(widths[index])
        for index, header in enumerate(headers))

    separator = "-+-".join("-" * width for width in widths)

    report.write(header_line + "\n")
    report.write(separator + "\n")

    for row in formatted_rows:
        report.write(
            " | ".join(
                value.ljust(widths[index])
                for index, value in enumerate(row)) + "\n")

# Text report about results of analyze
with open(REPORT_PATH, "w", encoding="utf-8") as report:

    report.write("=" * 80 + "\n")
    report.write("EXPLORATORNÍ ANALÝZA DATASETU (EDA)\n")
    report.write("=" * 80 + "\n")
    report.write(f"Počet řádků: {df.shape[0]}\n")
    report.write(f"Počet sloupců: {df.shape[1]}\n")