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

df.columns = [
    "url",
    "nazev_pneumatiky",
    "cena",
    "sirka",
    "profil",
    "index_nosnosti",
    "hloubka_dezenu",
    "provedeni_bocnice",
]

df["cena"] = pandas.to_numeric(
    df["cena"].astype("string").str.replace("$", "", regex=False),
    errors="coerce"
)

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

    write_section(report, "EXPLORATORY DATA ANALYSIS")

    # overall overview
    write_subsection(report, "Celkovy prehled")

    write_field(report, "Pocet radku:", len(df))
    write_field(report, "Pocet sloupcu:", len(df.columns))
    write_field(report, "Pocet chybejicich hodnot:", int(df.isna().sum().sum()))
    write_field(report, "Pocet duplicitnich radku:", int(df.duplicated().sum()))

    write_table(report,
        ["Parametr", "Datovy typ", "Pocet hodnot", "Unikatni hodnoty", "Chybejici hodnoty"],
        [
            [
                column,
                str(df[column].dtype),
                int(df[column].count()),
                int(df[column].nunique()),
                int(df[column].isna().sum()),
            ]
            for column in df.columns
        ],
    )

    # Missing values
    write_subsection(report, "Chybejici hodnoty")

    missing = df.isna().sum()
    missing = missing[missing > 0].sort_values(ascending=False)

    if missing.empty:
        report.write("Dataset neobsahuje zadne chybejici hodnoty.\n")
    else:
        for column, count in missing.items():
            write_field(
                report,
                column,
                f"{count} ({count / len(df) * 100:.2f} %)",
            )

    rows_with_missing = int(df.isna().any(axis=1).sum())
    rows_with_multiple_missing = int((df.isna().sum(axis=1) > 1).sum())

    write_field(report, "Radky s chybejici hodnotou:", rows_with_missing)
    write_field(report, "Radky s vice chybejicimi hodnotami:", rows_with_multiple_missing)

    # Numeric parameters
    write_subsection(report, "Statistika numerickych parametru")

    numeric_df = df.select_dtypes(include="number")

    if numeric_df.empty:
        report.write(
            "Zadne sloupce zatim nejsou rozpoznany jako numericke. "
            "Cenu a dalsi ciselne atributy je potreba nejprve prevadet na cisla.\n"
        )
    else:
        write_table(
            report,
            ["Parametr", "Minimum", "Maximum", "Prumer", "Median", "Smerodatna odchylka"],
            [
                [
                    column,
                    values.min(),
                    values.max(),
                    round(values.mean(), 2),
                    round(values.median(), 2),
                    round(values.std(), 2),
                ]
                for column, values in numeric_df.items()
            ],
        )

    # Most common values
    write_subsection(report, "Nejcastější hodnoty kategorickych parametru")

    for column in df.select_dtypes(include=["object", "string", "category"]).columns:
        if column == "url":
            continue

        report.write(f"\n{column}:\n")
        for value, count in df[column].value_counts(dropna=False).head(5).items():
            report.write(f"  {format_value(value)}: {count}\n")

    # Correllation
    write_subsection(report, "Korelacni analyza")

    if numeric_df.shape[1] >= 2:
        correlation = numeric_df.corr()
        write_table(
            report,
            ["Parametr"] + list(correlation.columns),
            [
                [column] + [round(value, 3) for value in correlation.loc[column]]
                for column in correlation.columns
            ],
        )
    else:
        report.write(
            "Pro korelacni analyzu jsou potreba alespon dva numericke parametry.\n"
        )
