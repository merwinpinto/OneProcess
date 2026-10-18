import pandas as pd
import plotly.express as px

class GraphAnalyzer:
    @staticmethod
    def create_bar_chart(
        df: pd.DataFrame,
        x_col: str,
        y_col: str,
        title: str = "Bar Chart",
        aggregation: str = "sum"
    ):
        """Generates an interactive Plotly bar chart with aggregation."""
        if aggregation == "sum":
            grouped_df = df.groupby(x_col, as_index=False)[y_col].sum()
        elif aggregation == "mean":
            grouped_df = df.groupby(x_col, as_index=False)[y_col].mean()
        elif aggregation == "count":
            grouped_df = df.groupby(x_col, as_index=False)[y_col].count()
        else:
            grouped_df = df

        fig = px.bar(
            grouped_df,
            x=x_col,
            y=y_col,
            title=title,
            labels={x_col: x_col, y_col: f"{y_col} ({aggregation})"},
            template="plotly_white"
        )
        return fig