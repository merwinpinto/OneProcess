# OneProcess

[![PyPI version](https://img.shields.io/pypi/v/oneprocess.svg)](https://pypi.org/project/oneprocess/)
[![Python Versions](https://img.shields.io/pypi/pyversions/oneprocess.svg)](https://pypi.org/project/oneprocess/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

**OneProcess** is a unified, one-stop data processing toolkit built for Data Analysts and Data Engineers. It eliminates the boilerplate code needed for everyday file wrangling, database synchronization (MySQL & Google BigQuery), schema inspection, and exploratory data visualization.

---

## Key Capabilities

### 1. Database & Cloud Ingestion (Loaders)
* **BigQuery Loader:** Push cleaned CSV/Excel files and DataFrames directly into Google Cloud BigQuery datasets and tables.
* **MySQL Loader:** Streamline bulk ingestion of processed flat files into relational MySQL tables.

### 2. Cloud & Database Extraction (Extractors)
* **MySQL to File:** Query MySQL databases and extract results straight into structured Excel (`.xlsx`) or CSV (`.csv`) files.
* **BigQuery to File:** Run analytical queries on GCP BigQuery and dump query outputs directly to local CSV or Excel files.

### 3. File Processing & Cleaning (Excel & CSV)
* **Deduplication Tool:** Drop duplicate rows globally or based on specified primary key columns.
* **Filtering Tool:** Query and filter rows using logical criteria and export targeted records.
* **Subset Creation:** Extract targeted columns and sliced segments into newly generated files.
* **Data Column Type Identifier:** Inspect files to detect data types, identify missing values, and map inferred schemas.
* **File Merging Tool** Merge two file type together having same colums.

### 4. Graph & Visual Analysis
* **Bar Graphs & Section Notes:** Generate bar charts for categorical metrics, distribution analysis, and export chart summaries with notes.

---

## Installation

```bash
# Standard installation
pip install oneprocess

# Complete installation with GCP BigQuery and MySQL drivers
pip install oneprocess[all]
