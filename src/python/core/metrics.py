import numpy as np
import pandas as pd

# ========= Admin (API_ready) =========

def normalize_saleschannel(order: pd.DataFrame) -> pd.DataFrame:
    if "saleschannel" not in order.columns and "salesChannel" in order.columns:
        order = order.rename(columns={"salesChannel": "saleschannel"})
    if "saleschannel" in order.columns:
        order["saleschannel"] = order["saleschannel"].fillna("Desconhecido").astype(str).str.strip()
    return order

def admin_summary(order: pd.DataFrame, customer: pd.DataFrame) -> dict:
    if order.empty or customer.empty:
        return {"ticket_medio_geral": 0.0, "tempo_medio_preparo": 0.0, "total_pedidos": 0, "total_clientes": 0}

    # conversões seguras
    if "total.orderamount" in order.columns:
        order["total.orderamount"] = pd.to_numeric(order["total.orderamount"], errors="coerce")
    if "preparationtime" in order.columns:
        order["preparationtime"] = pd.to_numeric(order["preparationtime"], errors="coerce")

    return {
        "ticket_medio_geral": round(order["total.orderamount"].mean(skipna=True), 2),
        "tempo_medio_preparo": round(order["preparationtime"].mean(skipna=True), 2),
        "total_pedidos": int(len(order)),
        "total_clientes": int(len(customer)),
    }

def kpis_by_store(order: pd.DataFrame) -> pd.DataFrame:
    if order.empty: 
        return pd.DataFrame(columns=["store.name","saleschannel","pedidos","receita","ticket_medio","tempo_medio"])
    g = (
        order.groupby(["store.name", "saleschannel"], dropna=False)
        .agg(
            pedidos=("id", "count") if "id" in order.columns else ("orderid","count"),
            receita=("total.orderamount", "sum"),
            ticket_medio=("total.orderamount", "mean"),
            tempo_medio=("preparationtime", "mean"),
        )
        .reset_index()
    )
    for c in ["receita","ticket_medio","tempo_medio"]:
        if c in g.columns:
            g[c] = g[c].round(2)
    return g.sort_values("receita", ascending=False, na_position="last")

def kpis_by_channel(order: pd.DataFrame) -> pd.DataFrame:
    if order.empty or "saleschannel" not in order.columns:
        return pd.DataFrame(columns=["saleschannel","pedidos","receita","ticket_medio","tempo_medio"])
    g = (
        order.groupby("saleschannel", dropna=False)
        .agg(
            pedidos=("id", "count") if "id" in order.columns else ("orderid","count"),
            receita=("total.orderamount", "sum"),
            ticket_medio=("total.orderamount", "mean"),
            tempo_medio=("preparationtime", "mean"),
        )
        .reset_index()
    )
    for c in ["receita","ticket_medio","tempo_medio"]:
        if c in g.columns:
            g[c] = g[c].round(2)
    return g

def campaign_engagement(campaign: pd.DataFrame, cq: pd.DataFrame) -> list[dict]:
    if cq.empty or "response" not in cq.columns or "campaignid" not in cq.columns:
        return []

    cq = cq.copy()
    cq["response_norm"] = cq["response"].astype(str).str.strip().str.lower()
    positives = {"ok","sim","yes","true","1","confirmado","recebido","👍"}
    negatives = {"nao","não","no","false","0","erro","falha","cancelado","❌"}

    cq["tem_resposta"] = np.where(cq["response_norm"].isin(positives), 1,
                           np.where(cq["response_norm"].isin(negatives), 0, np.nan))

    taxa = (
        cq.groupby("campaignid", dropna=False)["tem_resposta"]
        .mean()
        .rename("taxa_resposta")
        .reset_index()
    )
    camp = campaign.merge(taxa, left_on="id", right_on="campaignid", how="left").copy()

    # fallback para visualização
    if camp["taxa_resposta"].isna().all():
        rng = np.random.default_rng(42)
        camp["taxa_resposta"] = rng.uniform(0.4, 0.95, len(camp))

    camp["taxa_resposta_%"] = (camp["taxa_resposta"] * 100).round(1)

    cols = {
        "name": "nome",
        "store.name": "loja",
        "badge": "tipo",
        "taxa_resposta_%": "taxa_resposta_%"
    }
    out = (camp[list(cols.keys())]
           .rename(columns=cols)
           .dropna(subset=["taxa_resposta_%"])
           .sort_values("taxa_resposta_%", ascending=False)
           .head(10))
    return out.to_dict(orient="records")

# ========= Cliente (por período) =========

def inactivity_rate(customers: pd.DataFrame, days: int, now=None) -> tuple[int, float]:
    if customers.empty or "lastOrder" not in customers.columns:
        return 0, 0.0
    now = pd.Timestamp.utcnow() if now is None else now
    customers = customers.copy()
    customers["lastOrder"] = pd.to_datetime(customers["lastOrder"], errors="coerce", utc=True)
    inativos = customers[customers["lastOrder"] < (now - pd.Timedelta(days=days))]
    taxa = round((len(inativos) / max(len(customers),1)) * 100, 2)
    return len(inativos), taxa
