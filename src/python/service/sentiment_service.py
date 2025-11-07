import pandas as pd
import re
from textblob import TextBlob

def analisar_sentimentos(messages_df: pd.DataFrame) -> dict:
    """
    Analisa o sentimento das respostas dos clientes contidas em messages_df['response'].
    Usa TextBlob (polarity) e classificação manual complementar em português.
    Retorna um dicionário com % de sentimentos positivos, neutros e negativos.
    """

    # Garante que o DataFrame tem a coluna 'response'
    if messages_df.empty or "response" not in messages_df.columns:
        return {"positivo": 0, "neutro": 0, "negativo": 0}

    # Filtra apenas respostas não vazias
    responses = messages_df["response"].dropna().astype(str)
    if responses.empty:
        return {"positivo": 0, "neutro": 0, "negativo": 0}

    positivos, negativos, neutros = 0, 0, 0

    # Dicionário simples de reforço para expressões comuns em português
    palavras_positivas = [
        "gostei", "amei", "ótimo", "excelente", "obrigado", "obrigada", "bom", "maravilhoso", "😍", "😁", "👍"
    ]
    palavras_negativas = [
        "ruim", "péssimo", "demora", "caro", "horrível", "não", "interesse", "😡", "😠", "👎"
    ]

    for frase in responses:
        texto = frase.lower()

        # Detecção manual rápida
        if any(p in texto for p in palavras_positivas):
            positivos += 1
            continue
        if any(n in texto for n in palavras_negativas):
            negativos += 1
            continue

        # Fallback: usa TextBlob (inglês, mas funciona com base gramatical simples)
        # traduz pra inglês pra evitar erro em pt
        try:
            blob = TextBlob(texto)
            polaridade = blob.sentiment.polarity
        except Exception:
            polaridade = 0

        if polaridade > 0.1:
            positivos += 1
        elif polaridade < -0.1:
            negativos += 1
        else:
            neutros += 1

    total = max(positivos + negativos + neutros, 1)

    resultado = {
        "positivo": round((positivos / total) * 100, 1),
        "neutro": round((neutros / total) * 100, 1),
        "negativo": round((negativos / total) * 100, 1),
    }

    return resultado
