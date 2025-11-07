def admin_recommendations(summary: dict, campanhas_resumo: list[dict]) -> list[dict]:
    recs = []
    def add(msg, prio): recs.append({"mensagem": msg, "prioridade": prio})

    if summary.get("ticket_medio_geral", 0) < 70:
        add("💡 Ticket médio abaixo da média — teste combos e descontos progressivos.", "alta")
    if summary.get("tempo_medio_preparo", 0) > 40:
        add("⏱️ Tempo de preparo alto — investigue gargalos na cozinha.", "alta")
    if summary.get("total_pedidos", 0) < 50:
        add("📉 Poucos pedidos — rode campanhas de engajamento regional.", "alta")

    if campanhas_resumo:
        melhor = campanhas_resumo[0].get("nome", "N/A")
        add(f"📈 A campanha '{melhor}' performou bem — reutilize a copy/layout.", "media")

    if not recs:
        add("✅ Tudo dentro do esperado.", "baixa")
    return recs
