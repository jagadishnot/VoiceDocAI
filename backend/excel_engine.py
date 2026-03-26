import pandas as pd
import numpy as np

def process_excel(file_path):

    try:
        df = pd.read_excel(file_path)

        if df.empty:
            return {"error": "Excel file is empty"}

        # -----------------------------------------
        # Clean column names
        # -----------------------------------------
        df.columns = df.columns.str.strip()

        # -----------------------------------------
        # SMART DATE DETECTION (SAFE VERSION)
        # -----------------------------------------
        date_columns = []

        for col in df.columns:
            if df[col].dtype == "object":

                converted = pd.to_datetime(df[col], errors="coerce")

                success_ratio = converted.notna().sum() / len(df)

                if success_ratio > 0.7:
                    df[col] = converted
                    date_columns.append(col)

        # -----------------------------------------
        # Detect column types
        # -----------------------------------------
        numeric_columns = df.select_dtypes(include=np.number).columns.tolist()
        categorical_columns = df.select_dtypes(include=["object"]).columns.tolist()

        charts = []
        summary = {}
        missing_values = {}

        # -----------------------------------------
        # DATASET INFO
        # -----------------------------------------
        dataset_info = {
            "rows": int(df.shape[0]),
            "columns": int(df.shape[1])
        }

        # -----------------------------------------
        # MISSING VALUE ANALYSIS
        # -----------------------------------------
        for col in df.columns:
            missing_values[col] = int(df[col].isna().sum())

        charts.append({
            "type": "bar",
            "title": "Missing Data per Column",
            "x_label": "Column",
            "y_label": "Missing Count",
            "x": list(missing_values.keys()),
            "y": list(missing_values.values())
        })

        # -----------------------------------------
        # KPI SUMMARY (NUMERIC)
        # -----------------------------------------
        for col in numeric_columns:

            series = df[col].dropna()

            if series.empty:
                continue

            summary[col] = {
                "mean": round(float(series.mean()), 2),
                "median": round(float(series.median()), 2),
                "min": round(float(series.min()), 2),
                "max": round(float(series.max()), 2),
                "sum": round(float(series.sum()), 2),
                "std": round(float(series.std()), 2)
            }

        # -----------------------------------------
        # NUMERIC DISTRIBUTION (Histogram)
        # -----------------------------------------
        for col in numeric_columns:

            series = df[col].dropna()

            if series.empty:
                continue

            hist_counts, hist_bins = np.histogram(series, bins=10)

            charts.append({
                "type": "histogram",
                "title": f"{col} Distribution",
                "x_label": col,
                "y_label": "Frequency",
                "x": hist_bins[:-1].tolist(),
                "y": hist_counts.tolist()
            })

        # -----------------------------------------
        # CATEGORY vs NUMERIC (Revenue Comparison)
        # -----------------------------------------
        for cat in categorical_columns:
            for num in numeric_columns:

                grouped = df.groupby(cat)[num].sum().reset_index()

                if grouped.empty:
                    continue

                grouped = grouped.sort_values(by=num, ascending=False).head(10)

                charts.append({
                    "type": "bar",
                    "title": f"{cat} vs {num}",
                    "x_label": cat,
                    "y_label": f"Sum of {num}",
                    "x": grouped[cat].astype(str).tolist(),
                    "y": grouped[num].fillna(0).tolist()
                })

        # -----------------------------------------
        # CATEGORY DISTRIBUTION (Pie)
        # -----------------------------------------
        for cat in categorical_columns:

            counts = df[cat].value_counts().head(6)

            if counts.empty:
                continue

            charts.append({
                "type": "pie",
                "title": f"{cat} Distribution",
                "x_label": cat,
                "y_label": "Count",
                "x": counts.index.astype(str).tolist(),
                "y": counts.values.tolist()
            })

        # -----------------------------------------
        # NUMERIC TREND (Index Based)
        # -----------------------------------------
        for num in numeric_columns:

            charts.append({
                "type": "line",
                "title": f"{num} Trend",
                "x_label": "Index",
                "y_label": num,
                "x": list(range(len(df))),
                "y": df[num].fillna(0).tolist()
            })

        # -----------------------------------------
        # DATE BASED TREND (If Date Exists)
        # -----------------------------------------
        for date_col in date_columns:
            for num in numeric_columns:

                if df[date_col].isna().all():
                    continue

                grouped = df.groupby(date_col)[num].sum().reset_index()

                if grouped.empty:
                    continue

                charts.append({
                    "type": "line",
                    "title": f"{num} over {date_col}",
                    "x_label": date_col,
                    "y_label": f"Sum of {num}",
                    "x": grouped[date_col].astype(str).tolist(),
                    "y": grouped[num].fillna(0).tolist()
                })

        # -----------------------------------------
        # CORRELATION MATRIX
        # -----------------------------------------
        correlation_matrix = None

        if len(numeric_columns) > 1:
            correlation_matrix = (
                df[numeric_columns]
                .corr()
                .fillna(0)
                .round(2)
                .to_dict()
            )

        # -----------------------------------------
        # FINAL RESPONSE
        # -----------------------------------------
        return {
            "dataset_info": dataset_info,
            "columns": df.columns.tolist(),
            "numeric_columns": numeric_columns,
            "categorical_columns": categorical_columns,
            "date_columns": date_columns,
            "missing_values": missing_values,
            "summary": summary,
            "correlation_matrix": correlation_matrix,
            "charts": charts
        }

    except Exception as e:
        return {"error": str(e)}