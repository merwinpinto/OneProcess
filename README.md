# OneProcess

[![PyPI version](https://img.shields.io/pypi/v/oneprocess.svg)](https://pypi.org/project/oneprocess/)
[![Python Versions](https://img.shields.io/pypi/pyversions/oneprocess.svg)](https://pypi.org/project/oneprocess/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

**OneProcess** is a lightweight, unified data processing toolkit built for Data Analysts and Data Engineers. It eliminates the boilerplate code needed for everyday file wrangling, data cleaning, schema inspection, and exploratory data visualization.

---

## Key Capabilities

### 1. Schema & Column Type Identification
- **Schema Mapping:** Inspect files to infer data types, calculate missing value percentages, and preview samples across all columns.
- **Transposed Inspection Layout:** View field properties with dataset columns organized horizontally across the top for easy side-by-side comparison.

### 2. File Processing & Cleaning (CSV & Excel)
- **Deduplication Engine:** Identify duplicate entries with full row previews before dropping, configure first/last retention strategies, and target specific primary keys or the entire dataset.
- **Dynamic Multi-Column Filtering:** Automatically extract unique distinct values per column to filter records via intuitive dropdowns without writing manual queries.
- **Two-Stage Preview Workflow:** Inspect your raw data prior to changes, preview filtered matches in real time, and verify the resulting dataset before committing.
- **Dual Export Options:** Download cleaned and transformed datasets directly as CSV or Excel (`.xlsx`).

### 3. File Merging
- **Schema-Aligned Merging:** Combine multiple CSV or Excel files sharing matching column structures into a consolidated dataset.

### 4. Graph & Visual Analysis
- **Interactive Bar Charts:** Generate customizable Plotly bar charts with flexible aggregations (`sum`, `mean`, `count`) across categorical and numeric fields.
- **Insight Notes & Quick Reset:** Annotate charts with contextual observations and reset chart configurations instantly with a single click.

---

## Installation

```bash
# Core package installation
pip install oneprocess

## Installation
```bash
pip install oneprocess[streamlit]