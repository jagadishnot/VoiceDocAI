
import os
import uuid
import warnings

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


# Limits to reduce memory usage on Render's free instance
MAX_ROWS = 10_000
MAX_NUMERIC_CHARTS = 3
MAX_CATEGORICAL_CHARTS = 3
MAX_CORRELATION_COLUMNS = 8
MAX_HEATMAP_ROWS = 2_000
MAX_CHARTS = 12


def analyze_excel(file_path, output_dir):
    os.makedirs(output_dir, exist_ok=True)

    chart_paths = []
    insights = []

    # Avoid excessive Matplotlib memory use
    plt.ioff()

    # Read Excel data
    try:
        df = pd.read_excel(file_path)
    except Exception as exc:
        raise ValueError(f"Could not read Excel file: {exc}") from exc

    if df.empty:
        raise ValueError("The uploaded Excel file contains no data.")

    total_rows, total_cols = df.shape

    # Keep all rows for summary statistics, but sample large files
    # for charts to limit plotting overhead.
    if total_rows > MAX_ROWS:
        chart_df = df.sample(n=MAX_ROWS, random_state=42)
    else:
        chart_df = df

    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    categorical_cols = df.select_dtypes(
        include=["object", "category", "bool"]
    ).columns.tolist()

    def save_chart(fig):
        """Save a chart, close its figure, and return its URL."""
        filename = f"{uuid.uuid4().hex}.png"
        path = os.path.join(output_dir, filename)

        try:
            fig.savefig(
                path,
                format="png",
                dpi=80,
                bbox_inches="tight"
            )
        finally:
            plt.close(fig)

        chart_paths.append(f"/files/{filename}")

    try:
        # -------------------------
        # NUMERIC INSIGHTS
        # -------------------------
        for col in numeric_cols:
            series = pd.to_numeric(df[col], errors="coerce").dropna()

            if series.empty:
                continue

            insights.append({
                "column": str(col),
                "mean": float(series.mean()),
                "max": float(series.max()),
                "min": float(series.min())
            })

        # -------------------------
        # NUMERIC CHARTS
        # -------------------------
        for col in numeric_cols[:MAX_NUMERIC_CHARTS]:
            if len(chart_paths) >= MAX_CHARTS:
                break

            values = pd.to_numeric(
                chart_df[col], errors="coerce"
            ).dropna()

            if values.empty:
                continue

            # Trend chart
            fig, ax = plt.subplots(figsize=(7, 3))
            values.reset_index(drop=True).plot(ax=ax, linewidth=1)
            ax.set_title(f"{col} - Trend")
            ax.set_xlabel("Sample")
            ax.set_ylabel(str(col))
            fig.tight_layout()
            save_chart(fig)

            if len(chart_paths) >= MAX_CHARTS:
                break

            # Distribution chart
            fig, ax = plt.subplots(figsize=(7, 3))
            values.hist(ax=ax, bins=20)
            ax.set_title(f"{col} - Distribution")
            ax.set_xlabel(str(col))
            ax.set_ylabel("Frequency")
            fig.tight_layout()
            save_chart(fig)

            if len(chart_paths) >= MAX_CHARTS:
                break

            # Box plot
            fig, ax = plt.subplots(figsize=(6, 3))
            ax.boxplot(values, vert=True)
            ax.set_title(f"{col} - Boxplot")
            ax.set_ylabel(str(col))
            fig.tight_layout()
            save_chart(fig)

        # -------------------------
        # CATEGORICAL CHARTS
        # -------------------------
        for col in categorical_cols[:MAX_CATEGORICAL_CHARTS]:
            if len(chart_paths) >= MAX_CHARTS:
                break

            counts = (
                chart_df[col]
                .fillna("Missing")
                .astype(str)
                .value_counts()
                .head(10)
            )

            if counts.empty:
                continue

            # Top categories bar chart
            fig, ax = plt.subplots(figsize=(7, 4))
            counts.sort_values().plot(kind="barh", ax=ax)
            ax.set_title(f"{col} - Top Categories")
            ax.set_xlabel("Count")
            fig.tight_layout()
            save_chart(fig)

            if len(chart_paths) >= MAX_CHARTS:
                break

            # Category distribution pie chart
            pie_counts = counts.head(5)

            fig, ax = plt.subplots(figsize=(5, 4))
            pie_counts.plot(
                kind="pie",
                autopct="%1.1f%%",
                ax=ax
            )
            ax.set_title(f"{col} - Distribution")
            ax.set_ylabel("")
            fig.tight_layout()
            save_chart(fig)

        # -------------------------
        # CORRELATION HEATMAP
        # -------------------------
        if len(numeric_cols) > 1 and len(chart_paths) < MAX_CHARTS:
            corr_cols = numeric_cols[:MAX_CORRELATION_COLUMNS]

            correlation_data = chart_df[corr_cols].head(
                MAX_HEATMAP_ROWS
            )

            correlation = correlation_data.corr()

            fig, ax = plt.subplots(figsize=(7, 5))
            sns.heatmap(
                correlation,
                annot=len(corr_cols) <= 5,
                cmap="coolwarm",
                fmt=".2f",
                ax=ax
            )
            ax.set_title("Correlation Heatmap")
            fig.tight_layout()
            save_chart(fig)

        # -------------------------
        # MISSING VALUES CHART
        # -------------------------
        if len(chart_paths) < MAX_CHARTS:
            missing = df.isnull().sum()
            missing = missing[missing > 0].head(20)

            if not missing.empty:
                fig, ax = plt.subplots(figsize=(7, 4))
                missing.sort_values().plot(kind="bar", ax=ax)
                ax.set_title("Missing Values per Column")
                ax.set_ylabel("Missing Count")
                fig.tight_layout()
                save_chart(fig)

        # -------------------------
        # SIMPLE 3D VIEW
        # -------------------------
        if numeric_cols and len(chart_paths) < MAX_CHARTS:
            col = numeric_cols[0]

            values = pd.to_numeric(
                chart_df[col], errors="coerce"
            ).dropna().head(10)

            if not values.empty:
                from mpl_toolkits.mplot3d import Axes3D  # noqa: F401

                fig = plt.figure(figsize=(6, 4))
                ax = fig.add_subplot(111, projection="3d")

                xs = list(range(len(values)))
                ys = values.tolist()
                zs = [0] * len(values)

                ax.bar(xs, ys, zs=zs, zdir="y")
                ax.set_title(f"{col} - 3D View")
                ax.set_xlabel("Sample")
                ax.set_ylabel("Axis")
                ax.set_zlabel(str(col))
                fig.tight_layout()
                save_chart(fig)

    finally:
        # Close any remaining figures after success or failure
        plt.close("all")

    return {
        "total_rows": int(total_rows),
        "total_cols": int(total_cols),
        "insights": insights,
        "charts": chart_paths
    }
