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
        report.write("Zadne sloupce zatim nejsou rozpoznany jako numericke.\n")
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
        report.write("Pro korelacni analyzu jsou potreba alespon dva numericke parametry.\n")


# Graphs for attributes
# strings to numeric values
plot_df = df.copy()

# Width in mm: 255 or LT285.
# For floating dimensions, the width is taken from the profile, 12.50R = 317.5 mm.
plot_df["sirka_num"] = pandas.to_numeric(
    plot_df["sirka"]
    .astype("string")
    .str.extract(r"(\d{3})", expand=False),
    errors="coerce"
).astype(float)

flotation_width = pandas.to_numeric(
    plot_df["profil"]
    .astype("string")
    .str.extract(r"^\s*(\d{2}\.\d+)", expand=False),
    errors="coerce"
)

plot_df["sirka_num"] = plot_df["sirka_num"].fillna(
    flotation_width * 25.4
)

# Profile as a percentage value applies only to standard two-digit profiles.
# Values ​​such as 12.50R are not included here, as they signify something different
plot_df["profil_num"] = pandas.to_numeric(
    plot_df["profil"]
    .astype("string")
    .str.extract(r"^\s*(\d{2})(?=(?:ZR|R)?\s*$)", expand=False),
    errors="coerce"
)

plot_df["index_nosnosti_num"] = pandas.to_numeric(
    plot_df["index_nosnosti"],
    errors="coerce"
)

plot_df["hloubka_dezenu_num"] = pandas.to_numeric(
    plot_df["hloubka_dezenu"],
    errors="coerce"
)

# Histogram of prices
prices = plot_df["cena"].dropna()

matplotlib.pyplot.figure(figsize=(10, 6))

sns.histplot(data=prices, bins=20, kde=True)

matplotlib.pyplot.title("Rozložení cen pneumatik")
matplotlib.pyplot.xlabel("Cena ($)")
matplotlib.pyplot.ylabel("Počet záznamů")
matplotlib.pyplot.tight_layout()

matplotlib.pyplot.savefig(
    OUTPUT_DIR / "01_histogram_cen.png",
    dpi=300,
    bbox_inches="tight"
)

matplotlib.pyplot.close()

# Scatter plot - Tire width vs price
scatter_data = plot_df.dropna(subset=["sirka_num", "cena"])

matplotlib.pyplot.figure(figsize=(10, 6))

sns.scatterplot(
    data=scatter_data,
    x="sirka_num",
    y="cena",
    alpha=0.65
)

matplotlib.pyplot.title("Závislost ceny na šířce pneumatiky")
matplotlib.pyplot.xlabel("Šířka pneumatiky (mm)")
matplotlib.pyplot.ylabel("Cena ($)")
matplotlib.pyplot.tight_layout()

matplotlib.pyplot.savefig(
    OUTPUT_DIR / "02_sirka_vs_cena.png",
    dpi=300,
    bbox_inches="tight"
)

matplotlib.pyplot.close()

# Tread depth box plot
tread_depth = plot_df["hloubka_dezenu_num"].dropna()

matplotlib.pyplot.figure(figsize=(10, 5))

sns.boxplot(x=tread_depth, color="steelblue")

matplotlib.pyplot.title("Rozložení hodnot hloubky dezénu")
matplotlib.pyplot.xlabel("Hloubka dezénu")
matplotlib.pyplot.tight_layout()

matplotlib.pyplot.savefig(
    OUTPUT_DIR / "03_boxplot_hloubky_dezenu.png",
    dpi=300,
    bbox_inches="tight"
)

matplotlib.pyplot.close()

# Violin plot - price by profile
matplotlib.pyplot.figure(figsize=(12, 6))

sns.violinplot(
    data=df,
    x="profil",
    y="cena",
    inner="quartile",
    cut=0
)

matplotlib.pyplot.title("Price Distribution by Tire Profile")
matplotlib.pyplot.xlabel("Tire Profile")
matplotlib.pyplot.ylabel("Price ($)")
matplotlib.pyplot.xticks(rotation=45)
matplotlib.pyplot.tight_layout()
matplotlib.pyplot.savefig(
    "proj2/vystupy/04_violin_cena_podle_profilu.png",
    dpi=300
)
matplotlib.pyplot.close()

# 2 subgraphs: load index and sidewall construction
fig, axes = matplotlib.pyplot.subplots(1, 2, figsize=(15, 6))

# Left sub-graph: most frequent load-bearing index values
load_counts = (
    plot_df["index_nosnosti"]
    .dropna()
    .astype("string")
    .value_counts()
    .head(10)
    .sort_values()
)

axes[0].barh(load_counts.index, load_counts.values, color="steelblue")

axes[0].set_title("Nejčastější hodnoty indexu nosnosti")
axes[0].set_xlabel("Počet záznamů")
axes[0].set_ylabel("Index nosnosti")

# Right sub-graph: most common tire profiles
profile_counts = (
    plot_df["profil"]
    .fillna("Chybějící hodnota")
    .astype("string")
    .value_counts()
    .head(10)
    .sort_values()
)

axes[1].barh(
    profile_counts.index,
    profile_counts.values,
    color="darkorange"
)

axes[1].set_title("Zastoupení profilů pneumatik")
axes[1].set_xlabel("Počet záznamů")
axes[1].set_ylabel("Profil pneumatiky")

fig.suptitle("Srovnání atributů pneumatik", fontsize=14)
fig.tight_layout()

fig.savefig(
    OUTPUT_DIR / "05_srovnani_atributu.png",
    dpi=300,
    bbox_inches="tight"
)

matplotlib.pyplot.close(fig)

# Correlation heatmap
correlation_data = plot_df[
    [
        "cena",
        "sirka_num",
        "profil_num",
        "index_nosnosti_num",
        "hloubka_dezenu_num",
    ]
].copy()

correlation_data = correlation_data.rename(columns={
    "cena": "Cena",
    "sirka_num": "Sirka (mm)",
    "profil_num": "Profil (%)",
    "index_nosnosti_num": "Index nosnosti",
    "hloubka_dezenu_num": "Hloubka dezenu",
})

correlation_matrix = correlation_data.corr(method="spearman")

matplotlib.pyplot.figure(figsize=(10, 8))

sns.heatmap(
    correlation_matrix,
    annot=True,
    cmap="coolwarm",
    vmin=-1,
    vmax=1,
    center=0,
    fmt=".2f",
    linewidths=0.5
)

matplotlib.pyplot.title("Spearmanova korelacni matice")
matplotlib.pyplot.tight_layout()

matplotlib.pyplot.savefig(
    OUTPUT_DIR / "06_korelacni_heatmapa.png",
    dpi=300,
    bbox_inches="tight"
)

matplotlib.pyplot.close()

# Outlier detection: IQR and Z-score
with open(REPORT_PATH, "a", encoding="utf-8") as report:
    write_section(report, "ANALYZA ODLEHLYCH HODNOT")

    report.write(
        "Odlehle hodnoty jsou hledany dvema metodami: IQR a Z-skore.\n"
        "IQR oznaci hodnoty mimo interval Q1 - 1.5*IQR a Q3 + 1.5*IQR.\n"
        "Z-skore oznaci hodnoty s absolutni hodnotou vyssi nez 3.\n"
    )

    outlier_columns = {
        "cena": "cena",
        "hloubka_dezenu_num": "hloubka dezenu",
        "sirka_num": "sirka (mm)",
    }

    for column, label in outlier_columns.items():
        values = pandas.to_numeric(
            plot_df[column],
            errors="coerce"
        ).dropna()

        write_subsection(report, f"Odlehle hodnoty: {label}")

        if len(values) < 4:
            report.write("Nedostatek platnych hodnot pro spolehlivou analyzu.\n")
            continue

        q1 = values.quantile(0.25)
        q3 = values.quantile(0.75)
        iqr = q3 - q1

        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr

        iqr_mask = (
            (plot_df[column] < lower_bound)
            | (plot_df[column] > upper_bound)
        ).fillna(False)

        std = values.std(ddof=0)

        if std > 0:
            z_scores = (plot_df[column] - values.mean()) / std
            z_mask = z_scores.abs() > 3
            z_mask = z_mask.fillna(False)
        else:
            z_mask = pandas.Series(
                False,
                index=plot_df.index
            )

        write_field(report, "Pocet platnych hodnot:", len(values))
        write_field(report, "Q1:", round(q1, 3))
        write_field(report, "Q3:", round(q3, 3))
        write_field(report, "IQR:", round(iqr, 3))
        write_field(report, "Dolni hranice IQR:", round(lower_bound, 3))
        write_field(report, "Horni hranice IQR:", round(upper_bound, 3))
        write_field(report, "Odlehle hodnoty podle IQR:", int(iqr_mask.sum()))
        write_field(report, "Odlehle hodnoty podle Z-skore:", int(z_mask.sum()))

        for method_name, mask in [
            ("IQR", iqr_mask),
            ("Z-skore", z_mask),
        ]:
            report.write(f"\nHodnoty oznacene metodou {method_name}:\n")

            outliers = plot_df.loc[
                mask,
                ["nazev_pneumatiky", column]
            ]

            if outliers.empty:
                report.write("  Nebyly nalezeny zadne hodnoty.\n")
            else:
                for _, row in outliers.iterrows():
                    report.write(
                        f"  {row['nazev_pneumatiky']}: "
                        f"{row[column]}\n"
                    )