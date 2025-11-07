import pandas as pd
from reportlab.platypus import SimpleDocTemplate, Table
from reportlab.lib.pagesizes import A4
import os

EXPORT_DIR = os.path.join(os.path.dirname(__file__), "../exports")
os.makedirs(EXPORT_DIR, exist_ok=True)

def export_data(df: pd.DataFrame, name: str, fmt: str = "csv"):
    """Exporta DataFrame em CSV, XLSX ou PDF."""
    if df.empty:
        print(f"⚠️ Nenhum dado para exportar: {name}")
        return

    path = os.path.join(EXPORT_DIR, f"{name}.{fmt}")

    if fmt == "csv":
        df.to_csv(path, index=False)
    elif fmt == "xlsx":
        df.to_excel(path, index=False)
    elif fmt == "pdf":
        doc = SimpleDocTemplate(path, pagesize=A4)
        data = [df.columns.tolist()] + df.values.tolist()
        doc.build([Table(data)])

    print(f"✅ Arquivo exportado: {path}")
