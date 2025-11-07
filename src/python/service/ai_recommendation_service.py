# src/python/service/ai_recommendation_service.py

from __future__ import annotations
import numpy as np
import pandas as pd
from datetime import datetime, timedelta


# =========================
# Helpers robustos
# =========================
def _as_dt(s: pd.Series, fallback: str | None = None) -> pd.Series:
    """Converte série para datetime de forma resiliente."""
    if s is None:
        return pd.Series(dtype="datetime64[ns]")
    out = pd.to_datetime(s, errors="coerce", utc=True)
    if out.isna().all() and fallback and fallback in s.index:
        out = pd.to_datetime(s[fallback], errors="coerce", utc=True)
    return out

def _col(df: pd.DataFrame, *names, default=None):
    """Retorna a primeira coluna existente dentre names; senão, default."""
    for n in names:
        if n in df.columns:
            return df[n]
    if callable(default):
        return default()
    return default

def _safe_ratio(num, den, pct=False, round_nd=2):
    den = den if den not in (None, 0, np.nan) else 1
    val = float(num) / float(den)
    if pct:
        val *= 100.0
    return round(val, round_nd)

def _nonempty(df: pd.DataFrame) -> bool:
    return isinstance(df, pd.DataFrame) and (len(df) > 0)


# =========================
# Núcleo de recomendações
# =========================
def _recs_por_canais(campaigns: pd.DataFrame, orders: pd.DataFrame) -> list[str]:
    recs = []

    # 1) Desempenho de campanhas por canal (se houver)
    if _nonempty(campaigns):
        channel = _col(campaigns, "channel", "deliveryChannel", default=pd.Series(dtype=str))
        sent = _col(campaigns, "sent", "messagesSent", default=pd.Series(0, index=campaigns.index))
        delivered = _col(campaigns, "delivered", "messagesDelivered", default=pd.Series(0, index=campaigns.index))
        df = pd.DataFrame({"channel": channel, "sent": pd.to_numeric(sent, errors="coerce").fillna(0),
                           "delivered": pd.to_numeric(delivered, errors="coerce").fillna(0)})
        if not df.empty and "channel" in df and df["channel"].notna().any():
            ch = (df.groupby("channel", dropna=True)
                    .agg(sent=("sent","sum"), delivered=("delivered","sum"))
                    .reset_index())
            ch["taxa_entrega_%"] = (ch["delivered"] / ch["sent"].replace(0, np.nan) * 100).fillna(0).round(1)
            ch = ch.sort_values(["taxa_entrega_%", "delivered"], ascending=[False, False])
            if not ch.empty:
                top = ch.iloc[0]
                recs.append(f"📣 Priorize o canal **{top['channel']}**: taxa de entrega {top['taxa_entrega_%']}% (melhor entre os canais).")
                # Se existir um segundo canal, sugerir teste A/B
                if len(ch) > 1:
                    sec = ch.iloc[1]
                    recs.append(
                        f"🧪 Faça A/B {top['channel']} vs {sec['channel']} em uma régua curta (3–5 dias) para validar conversão real."
                    )

    # 2) Foco em canal que mais gera receita em pedidos (quando existir)
    if _nonempty(orders) and "saleschannel" in orders.columns:
        oc = orders.copy()
        oc["valor"] = pd.to_numeric(_col(oc, "totalAmount", "total", default=pd.Series(0, index=oc.index)), errors="coerce").fillna(0)
        top_sales = (oc.groupby("saleschannel", dropna=True)["valor"]
                       .sum()
                       .sort_values(ascending=False))
        if not top_sales.empty:
            best_sc = top_sales.index[0]
            best_val = top_sales.iloc[0]
            recs.append(
                f"💰 Canal com maior faturamento recente: **{best_sc}** (R$ {best_val:,.2f}). Direcione as melhores ofertas por este canal."
                .replace(",", "X").replace(".", ",").replace("X", ".")
            )

    return recs


def _recs_por_janela_horaria(campaigns: pd.DataFrame, orders: pd.DataFrame) -> list[str]:
    recs = []

    # Tentamos horário de ENVIO das campanhas
    if _nonempty(campaigns):
        send_time = None
        for col in ["sendTime", "createdAt", "sentAt", "created_at", "scheduledAt"]:
            if col in campaigns.columns:
                send_time = _as_dt(campaigns[col])
                break
        if send_time is not None and not send_time.isna().all():
            tmp = pd.DataFrame({"h": send_time.dt.hour})
            tmp = tmp.dropna()
            if not tmp.empty:
                top_hour = int(tmp["h"].value_counts().idxmax())
                recs.append(
                    f"🕒 Agende disparos entre **{top_hour:02d}h–{(top_hour+1)%24:02d}h**: maior concentração de envios bem-sucedidos."
                )

    # Se não houver horário em campanhas, tentar horário de pedidos
    if not recs and _nonempty(orders):
        dt = None
        for col in ["createdAt", "orderDate", "created_at", "date"]:
            if col in orders.columns:
                dt = _as_dt(orders[col])
                break
        if dt is not None and not dt.isna().all():
            dfh = pd.DataFrame({"h": dt.dt.hour})
            top_hour = int(dfh["h"].value_counts().idxmax())
            recs.append(
                f"🕒 Dispare campanhas perto de **{top_hour:02d}h** (pico de pedidos)."
            )

    return recs


def _recs_por_segmento(customers: pd.DataFrame) -> list[str]:
    recs = []
    if not _nonempty(customers):
        return recs

    seg = _col(customers, "segment", default=pd.Series("", index=customers.index)).astype(str).str.lower()
    is_vip = _col(customers, "isVIP", default=pd.Series(False, index=customers.index)).astype(bool)
    status = _col(customers, "status", default=pd.Series("", index=customers.index)).astype(str)
    last_order = _as_dt(_col(customers, "lastOrder", "last_order"))

    # 1) VIPs
    n_vip = int(is_vip.sum())
    if n_vip > 0:
        recs.append(f"👑 **VIPs ({n_vip})** respondem melhor a vantagens exclusivas. Teste: frete grátis + acesso antecipado a novidades.")

    # 2) Fiéis (loyal)
    n_loyal = int(seg.eq("loyal").sum())
    if n_loyal > 0:
        recs.append(f"💚 **Fiéis ({n_loyal})**: programe upgrade de benefício (ex.: pontos em dobro no próximo pedido).")

    # 3) Reativação (considera inativos por lastOrder)
    if last_order is not None and not last_order.isna().all():
        cutoff_45 = pd.Timestamp.utcnow() - pd.Timedelta(days=45)
        inativos = customers.loc[(last_order < cutoff_45) | (last_order.isna())]
        n_inativos = int(len(inativos))
        if n_inativos > 0:
            recs.append(
                f"🔄 **Reativação ({n_inativos})**: régua 2 passos — 1) WhatsApp com 10% OFF; 2) 72h depois, e-mail com **gatilho de escassez**."
            )

    # 4) Ticket médio baixo — empurrar combos
    avg_ticket = pd.to_numeric(_col(customers, "avgTicket", default=pd.Series(np.nan, index=customers.index)), errors="coerce")
    if avg_ticket.notna().any():
        p25, p75 = np.nanpercentile(avg_ticket.dropna(), [25, 75])
        low_segment = int((avg_ticket <= p25).sum())
        high_segment = int((avg_ticket >= p75).sum())
        if low_segment > 0:
            recs.append(f"🧩 Converta **ticket baixo ({low_segment} clientes)** com combos ‘leve 2 e ganhe 15%’.")
        if high_segment > 0:
            recs.append(f"💎 **Alto ticket ({high_segment})**: crie bundles premium com sobremesa extra e prioridade de preparo (upsell).")

    return recs


def _recs_por_campanhas_top(campaigns: pd.DataFrame) -> list[str]:
    recs = []
    if not _nonempty(campaigns):
        return recs

    # Melhor/pior por conversão (se existir)
    conv = pd.to_numeric(_col(campaigns, "conversionRate", "conversion", default=pd.Series(np.nan, index=campaigns.index)), errors="coerce")
    if conv.notna().any():
        idx_best = int(conv.idxmax())
        idx_worst = int(conv.idxmin())
        best = campaigns.loc[idx_best]
        worst = campaigns.loc[idx_worst]

        best_name = str(_col(best.to_frame().T, "name", "title", default=pd.Series("N/A")).iloc[0])
        worst_name = str(_col(worst.to_frame().T, "name", "title", default=pd.Series("N/A")).iloc[0])
        best_pct = float(conv.loc[idx_best] * 100.0)
        worst_pct = float(conv.loc[idx_worst] * 100.0)

        recs.append(f"🏆 Melhor campanha recente: **{best_name}** ({best_pct:.1f}% conversão). Replique o criativo e o canal.")
        recs.append(f"⛔ Evite **{worst_name}** ({worst_pct:.1f}%); mantenha apenas como grupo de controle.")

    # Volume/entrega (se existir)
    sent = pd.to_numeric(_col(campaigns, "sent", "messagesSent", default=pd.Series(np.nan, index=campaigns.index)), errors="coerce")
    delivered = pd.to_numeric(_col(campaigns, "delivered", "messagesDelivered", default=pd.Series(np.nan, index=campaigns.index)), errors="coerce")
    if sent.notna().any() and delivered.notna().any():
        taxa = (delivered / sent.replace(0, np.nan) * 100).round(1)
        idx = int(taxa.idxmax())
        nm = str(_col(campaigns.loc[[idx]], "name", "title", default=pd.Series("Campanha")).iloc[0])
        recs.append(f"🚀 Maior taxa de entrega: **{nm}** ({float(taxa.loc[idx]):.1f}%). Reuse a segmentação/base.")

    return recs


def _recs_de_precificacao(orders: pd.DataFrame) -> list[str]:
    recs = []
    if not _nonempty(orders):
        return recs

    val = pd.to_numeric(_col(orders, "totalAmount", "total", default=pd.Series(np.nan, index=orders.index)), errors="coerce")
    if val.notna().sum() >= 10:
        q75 = np.nanpercentile(val.dropna(), 75)
        q25 = np.nanpercentile(val.dropna(), 25)
        spread = q75 - q25
        if spread > 0:
            recs.append(
                f"🎯 Teste ‘**preço-âncora**’: destaque item ~R$ {q75:,.2f} para puxar ticket médio."
                .replace(",", "X").replace(".", ",").replace("X", ".")
            )

    return recs


# =========================
# API pública
# =========================
def gerar_recomendacoes_inteligentes(
    campaigns: pd.DataFrame | None,
    orders: pd.DataFrame | None,
    customers: pd.DataFrame | None,
) -> list[str]:
    """
    Gera recomendações textuais com base em padrões observados em campanhas, pedidos e clientes.
    Tolerante a colunas ausentes; retorna sempre lista[str].
    """
    campaigns = campaigns if _nonempty(campaigns) else pd.DataFrame()
    orders = orders if _nonempty(orders) else pd.DataFrame()
    customers = customers if _nonempty(customers) else pd.DataFrame()

    recs = []
    try:
        recs += _recs_por_canais(campaigns, orders)
        recs += _recs_por_janela_horaria(campaigns, orders)
        recs += _recs_por_segmento(customers)
        recs += _recs_por_campanhas_top(campaigns)
        recs += _recs_de_precificacao(orders)
    except Exception as e:
        recs.append(f"⚙️ IA de campanhas em modo seguro: {e}")

    # Pós-processamento: remover duplicadas e polir
    clean = []
    seen = set()
    for r in recs:
        r = str(r).strip()
        if r and r not in seen:
            seen.add(r)
            clean.append(r)

    # Caso extremo: nada dedutível
    if not clean:
        clean = [
            "💡 Sugestão: execute uma régua de reativação (WhatsApp → E-mail) e um A/B de criativo no canal com maior faturamento."
        ]
    return clean
