"""
Core file processing, cleaning, schema inspection, and merging operations.
"""
from typing import List, Optional, Union
import io
import pandas as pd


class DataProcessor:
    def __init__(self, data: Union[str, pd.DataFrame, io.BytesIO], sheet_name: Optional[str] = None):
        """
        Initialize with a file path, BytesIO buffer (from Streamlit), or existing DataFrame.
        """
        if isinstance(data, pd.DataFrame):
            self.df = data.copy()
        elif isinstance(data, (str, io.BytesIO)):
            self.df = self.read_file(data, sheet_name=sheet_name)
        else:
            raise ValueError("Unsupported data source. Provide a file path, buffer, or DataFrame.")

    @staticmethod
    def read_file(source: Union[str, io.BytesIO], sheet_name: Optional[str] = None) -> pd.DataFrame:
        """Helper to read either CSV or Excel seamlessly."""
        if isinstance(source, str):
            if source.endswith((".xlsx", ".xls")):
                return pd.read_excel(source, sheet_name=sheet_name or 0)
            return pd.read_csv(source)
        else:
            # BytesIO stream from file uploaders
            try:
                return pd.read_csv(source)
            except Exception:
                source.seek(0)
                return pd.read_excel(source, sheet_name=sheet_name or 0)

    def identify_column_types(self) -> pd.DataFrame:
        """
        Inspect columns, detect data types, count nulls, and provide sample values.
        """
        summary = []
        for col in self.df.columns:
            series = self.df[col]
            null_count = int(series.isnull().sum())
            null_pct = round((null_count / len(self.df)) * 100, 2) if len(self.df) > 0 else 0
            
            # Inferred logical category
            dtype_str = str(series.dtype)
            if pd.api.types.is_numeric_dtype(series):
                category = "Numeric"
            elif pd.api.types.is_datetime64_any_dtype(series):
                category = "Datetime"
            elif pd.api.types.is_bool_dtype(series):
                category = "Boolean"
            else:
                category = "Categorical / Text"

            sample_val = str(series.dropna().iloc[0]) if not series.dropna().empty else "None"

            summary.append({
                "Column Name": col,
                "Inferred Category": category,
                "Pandas Dtype": dtype_str,
                "Missing Values": null_count,
                "Missing (%)": f"{null_pct}%",
                "Sample Value": sample_val
            })
        return pd.DataFrame(summary)

    def deduplicate(self, subset: Optional[List[str]] = None, keep: str = "first") -> pd.DataFrame:
        """Removes duplicate records based on optional primary key columns."""
        initial_count = len(self.df)
        self.df = self.df.drop_duplicates(subset=subset, keep=keep).reset_index(drop=True)
        return self.df

    def filter_data(self, query_string: str) -> pd.DataFrame:
        """Filter dataset rows using standard pandas query syntax."""
        self.df = self.df.query(query_string).reset_index(drop=True)
        return self.df

    def create_subset(self, columns: List[str], condition: Optional[str] = None) -> pd.DataFrame:
        """Extracts specified columns and optional filtered rows into a new DataFrame."""
        filtered_df = self.df.query(condition) if condition else self.df
        return filtered_df[columns].copy().reset_index(drop=True)

    @staticmethod
    def merge_files(
        first_source: Union[str, pd.DataFrame, io.BytesIO],
        second_source: Union[str, pd.DataFrame, io.BytesIO],
        how: str = "concat"
    ) -> pd.DataFrame:
        """
        Merges two files or DataFrames having identical or compatible columns.
        how: 'concat' (vertical stack) or 'inner' (only matching columns).
        """
        df1 = first_source if isinstance(first_source, pd.DataFrame) else DataProcessor.read_file(first_source)
        df2 = second_source if isinstance(second_source, pd.DataFrame) else DataProcessor.read_file(second_source)

        if how == "concat":
            merged = pd.concat([df1, df2], ignore_index=True)
        elif how == "inner":
            common_cols = [c for c in df1.columns if c in df2.columns]
            merged = pd.concat([df1[common_cols], df2[common_cols]], ignore_index=True)
        else:
            raise ValueError("Supported merge modes are 'concat' and 'inner'.")
        return merged