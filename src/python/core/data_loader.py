import os
import json
import pandas as pd

BASE_DATA_DIR = os.path.join(os.path.dirname(__file__), "../data")

def _path(*parts: str) -> str:
    return os.path.join(BASE_DATA_DIR, *parts)

def read_json_df(filename: str) -> pd.DataFrame:
    """Lê JSON em data/ e retorna DataFrame; tolera falhas."""
    try:
        with open(_path(filename), encoding="utf-8") as f:
            data = json.load(f)
        df = pd.json_normalize(data)
        return df
    except FileNotFoundError:
        print(f"⚠️ Arquivo não encontrado: {filename}")
        return pd.DataFrame()
    except Exception as e:
        print(f"⚠️ Erro lendo {filename}: {e}")
        return pd.DataFrame()

def read_text_json(filename: str):
    """Lê JSON cru (lista/dict) sem normalizar."""
    try:
        with open(_path(filename), encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None

def to_numeric(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    for c in cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    return df

def lower_strip_columns(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = df.columns.str.lower().str.strip()
    return df

# loaders “API_ready”
def load_api_ready():
    campaign = lower_strip_columns(read_json_df("Campaign_API_ready.json"))
    cq       = lower_strip_columns(read_json_df("CampaignQueue_API_ready.json"))
    customer = lower_strip_columns(read_json_df("Customer_API_ready.json"))
    order    = lower_strip_columns(read_json_df("Order_API_ready.json"))
    return campaign, cq, customer, order

# loaders por período (30d/60d/90d)
def load_period(period: str):
    orders    = read_json_df(f"orders_{period}.json")
    customers = read_json_df(f"customers_{period}.json")
    campaigns = read_json_df("campaigns.json")
    return orders, customers, campaigns
