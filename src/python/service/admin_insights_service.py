from core.data_loader import load_api_ready, to_numeric
from core.metrics import (
    normalize_saleschannel, admin_summary, kpis_by_store, kpis_by_channel, campaign_engagement
)
from core.recommendations import admin_recommendations

def generate_admin_dashboard(period: str = "30d") -> dict:
    campaign, cq, customer, order = load_api_ready()

    # normalizações
    order = normalize_saleschannel(order)
    order = to_numeric(order, ["total.orderamount", "preparationtime"])

    resumo = admin_summary(order, customer)
    lojas  = kpis_by_store(order).head(10).to_dict(orient="records")
    canais = kpis_by_channel(order).to_dict(orient="records")
    campanhas = campaign_engagement(campaign, cq)

    recomendacoes = admin_recommendations(resumo, campanhas)

    return {
        "restaurante": "Painel Administrativo Cannoli",
        "period": period,
        "resumo_geral": resumo,
        "lojas_top": lojas,
        "canais_venda": canais,
        "campanhas_resumo": campanhas,
        "recomendacoes": recomendacoes,
    }
