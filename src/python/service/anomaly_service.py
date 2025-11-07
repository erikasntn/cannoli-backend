import numpy as np
import pandas as pd

def detectar_anomalias(previsao: list[dict], limiar: float = 2.0) -> list[dict]:
    """Detecta valores fora do padrão (alta ou baixa anômala)."""
    if not previsao:
        return []

    valores = np.array([p["receita_prevista"] for p in previsao])
    media, desvio = np.mean(valores), np.std(valores)

    anomalias = []
    for p in previsao:
        z = (p["receita_prevista"] - media) / (desvio if desvio > 0 else 1)
        if abs(z) > limiar:
            anomalias.append({
                "data": p["data"],
                "valor": p["receita_prevista"],
                "tipo": "queda" if z < 0 else "pico"
            })
    return anomalias
