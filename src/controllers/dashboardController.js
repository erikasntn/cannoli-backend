import { getInsights } from "../services/dashboardService.js";
import { generateExport } from "../services/exportService.js";
import { runPythonScript } from "../utils/pythonRunner.js";
import path from "path";

export async function handleInsights(req, res) {
  try {
    const { period } = req.params;
    const { metric, channel, region } = req.query;
    const userRole = req.user?.role || "admin";

    const base = await getInsights(period, userRole);
    let lojas = base.lojas_top || [];

    if (channel && channel !== "all")
      lojas = lojas.filter((x) => (x.saleschannel || "").toLowerCase() === channel);
    if (region && region !== "all")
      lojas = lojas.filter(
        (x) => (x["delivery.region"] || x.region || "").toLowerCase() === region
      );

    res.json({ ...base, lojas_top: lojas });
  } catch (error) {
    console.error(error);
    res.status(500).json({ error: "Falha ao obter insights" });
  }
}

export async function handleAlerts(req, res) {
  try {
    const scriptPath = path.resolve("src/python/alerts.py");
    const result = await runPythonScript(scriptPath, [req.params.period]);
    res.json(JSON.parse(result));
  } catch (error) {
    res.status(500).json({ error: "Falha ao gerar alertas" });
  }
}

export async function handleExport(req, res) {
  try {
    await generateExport(req, res);
  } catch (error) {
    res.status(500).json({ error: "Falha ao exportar relatório" });
  }
}
