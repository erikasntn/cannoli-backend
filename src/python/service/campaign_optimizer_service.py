import pandas as pd

def otimizar_campanhas(campaigns: pd.DataFrame) -> dict:
    """Identifica canal, horário e tipo de campanha com melhor desempenho."""
    if campaigns.empty:
        return {}

    resultado = {}

    if "salesChannel" in campaigns.columns:
        canal = (
            campaigns.groupby("salesChannel")["conversionRate"]
            .mean()
            .sort_values(ascending=False)
            .head(1)
        )
        resultado["canal_ideal"] = canal.index[0]
        resultado["taxa_canal"] = round(canal.iloc[0] * 100, 2)

    if "hour" in campaigns.columns:
        hora = (
            campaigns.groupby("hour")["conversionRate"]
            .mean()
            .sort_values(ascending=False)
            .head(1)
        )
        resultado["horario_ideal"] = f"{int(hora.index[0]):02d}:00h"
        resultado["taxa_horario"] = round(hora.iloc[0] * 100, 2)

    if "type" in campaigns.columns:
        tipo = (
            campaigns.groupby("type")["conversionRate"]
            .mean()
            .sort_values(ascending=False)
            .head(1)
        )
        resultado["tipo_ideal"] = tipo.index[0]
        resultado["taxa_tipo"] = round(tipo.iloc[0] * 100, 2)

    return resultado
