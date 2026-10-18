import pandas as pd


class ColumnTypeIdentifier:
    """Utility class to analyze and inspect DataFrame schemas, missing values, and data types."""

    def __init__(self, df: pd.DataFrame):
        self.df = df

    def inspect(self) -> pd.DataFrame:
        """Inspects data types, missing values, uniqueness, and samples for all columns.
        
        Returns a DataFrame where:
          - Columns (X-axis): Your dataset's column names
          - Index (Y-axis): Metric names (Inferred Type, Missing Values, etc.)
        """
        metrics = {}
        total_count = len(self.df)

        for col in self.df.columns:
            missing_count = int(self.df[col].isna().sum())
            missing_pct = round((missing_count / total_count) * 100, 2) if total_count > 0 else 0.0
            unique_count = int(self.df[col].nunique())
            non_null_series = self.df[col].dropna()
            sample_val = str(non_null_series.iloc[0]) if not non_null_series.empty else "None"

            metrics[col] = {
                "Inferred Type": str(self.df[col].dtype),
                "Missing Values": missing_count,
                "Missing %": f"{missing_pct}%",
                "Unique Values": unique_count,
                "Sample": sample_val
            }

        # Converting dict to DataFrame naturally places column names at top and metric keys on the Y-axis
        result_df = pd.DataFrame(metrics)
        result_df.index.name = "Metric"
        return result_df