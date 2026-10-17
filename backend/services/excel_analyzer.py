import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import uuid
from mpl_toolkits.mplot3d import Axes3D


def analyze_excel(file_path, output_dir):
    df = pd.read_excel(file_path)

    insights = []
    chart_paths = []

    total_rows, total_cols = df.shape

    numeric_cols = df.select_dtypes(include="number").columns
    categorical_cols = df.select_dtypes(include="object").columns

    # -------------------------
    # 📊 INSIGHTS
    # -------------------------
    for col in numeric_cols:
        insights.append({
            "column": col,
            "mean": float(df[col].mean()),
            "max": float(df[col].max()),
            "min": float(df[col].min())
        })

    # -------------------------
    # 📈 NUMERIC VISUALS
    # -------------------------
    for col in numeric_cols:

        # 📈 LINE CHART (trend)
        plt.figure()
        df[col].plot(title=f"{col} - Trend")
        fname = f"{uuid.uuid4()}.png"
        path = os.path.join(output_dir, fname)
        plt.savefig(path)
        plt.close()
        chart_paths.append(f"/files/{fname}")

        # 📊 HISTOGRAM (distribution)
        plt.figure()
        df[col].hist()
        plt.title(f"{col} - Distribution")
        fname = f"{uuid.uuid4()}.png"
        path = os.path.join(output_dir, fname)
        plt.savefig(path)
        plt.close()
        chart_paths.append(f"/files/{fname}")

        # 📦 BOX PLOT (outliers)
        plt.figure()
        df.boxplot(column=col)
        plt.title(f"{col} - Boxplot")
        fname = f"{uuid.uuid4()}.png"
        path = os.path.join(output_dir, fname)
        plt.savefig(path)
        plt.close()
        chart_paths.append(f"/files/{fname}")

    # -------------------------
    # 🔥 CATEGORICAL VISUALS
    # -------------------------
    for col in categorical_cols:

        # 📊 BAR CHART
        plt.figure()
        df[col].value_counts().head(10).plot(kind="bar")
        plt.title(f"{col} - Top Categories")
        fname = f"{uuid.uuid4()}.png"
        path = os.path.join(output_dir, fname)
        plt.savefig(path)
        plt.close()
        chart_paths.append(f"/files/{fname}")

        # 🥧 PIE CHART
        plt.figure()
        df[col].value_counts().head(5).plot(kind="pie", autopct="%1.1f%%")
        plt.title(f"{col} - Distribution")
        plt.ylabel("")
        fname = f"{uuid.uuid4()}.png"
        path = os.path.join(output_dir, fname)
        plt.savefig(path)
        plt.close()
        chart_paths.append(f"/files/{fname}")

    # -------------------------
    # 🔥 CORRELATION HEATMAP
    # -------------------------
    if len(numeric_cols) > 1:
        plt.figure(figsize=(10, 7))
        sns.heatmap(
            df[numeric_cols].corr(),
            annot=True,
            cmap="coolwarm",
            fmt=".2f"
        )
        plt.title("Correlation Heatmap")

        fname = f"{uuid.uuid4()}.png"
        path = os.path.join(output_dir, fname)
        plt.savefig(path)
        plt.close()
        chart_paths.append(f"/files/{fname}")

    # -------------------------
    # 🔥 MISSING VALUES CHART
    # -------------------------
    missing = df.isnull().sum()
    if missing.sum() > 0:
        plt.figure()
        missing.plot(kind="bar")
        plt.title("Missing Values per Column")

        fname = f"{uuid.uuid4()}.png"
        path = os.path.join(output_dir, fname)
        plt.savefig(path)
        plt.close()
        chart_paths.append(f"/files/{fname}")

    # -------------------------
    # 🔥 3D BAR (ONLY FIRST COLUMN)
    # -------------------------
    if len(numeric_cols) > 0:
        col = numeric_cols[0]

        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')

        values = df[col].head(10).values
        xs = range(len(values))
        ys = values

        ax.bar(xs, ys, zs=0, zdir='y')

        ax.set_title(f"{col} - 3D View")

        fname = f"{uuid.uuid4()}.png"
        path = os.path.join(output_dir, fname)
        plt.savefig(path)
        plt.close()
        chart_paths.append(f"/files/{fname}")

    # -------------------------
    # RETURN
    # -------------------------
    return {
        "total_rows": total_rows,
        "total_cols": total_cols,
        "insights": insights,
        "charts": chart_paths
    }