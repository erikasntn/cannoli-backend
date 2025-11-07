import ExcelJS from "exceljs";
import PDFDocument from "pdfkit";
import { Parser as Json2Csv } from "json2csv";
import { getInsights } from "./dashboardService.js";

/**
 * Gera o relatório consolidado da Cannoli (CSV, XLSX ou PDF)
 * @route GET /api/export?type=csv|xlsx|pdf
 */
export async function generateExport(req, res) {
  const { type = "csv" } = req.query;
  const periods = ["30d", "60d", "90d"];
  const datasets = {};

  // 🔹 coleta todos os períodos
  for (const p of periods) {
    try {
      datasets[p] = await getInsights(p, "admin");
    } catch (err) {
      console.warn(`⚠️ Falha ao obter insights de ${p}:`, err.message);
      datasets[p] = null;
    }
  }

  // 🔹 exporta no formato solicitado
  switch (type) {
    case "xlsx":
      return generateExcel(datasets, res);
    case "pdf":
      return generatePDF(datasets, res);
    default:
      return generateCSV(datasets, res);
  }
}

/* ========== CSV ========== */
function generateCSV(datasets, res) {
  const parser = new Json2Csv();
  const combined = [];

  for (const [period, data] of Object.entries(datasets)) {
    if (!data?.lojas_top) continue;
    data.lojas_top.forEach((item) => combined.push({ period, ...item }));
  }

  const csv = parser.parse(combined);
  res
    .status(200)
    .setHeader("Content-Type", "text/csv; charset=utf-8")
    .setHeader("Content-Disposition", 'attachment; filename="relatorio_cannoli.csv"')
    .send(csv);
}

/* ========== XLSX ========== */
async function generateExcel(datasets, res) {
  const wb = new ExcelJS.Workbook();

  for (const [period, data] of Object.entries(datasets)) {
    if (!data) continue;

    const ws1 = wb.addWorksheet(`Lojas ${period}`);
    ws1.columns = [
      { header: "Loja", key: "store.name", width: 30 },
      { header: "Pedidos", key: "pedidos", width: 12 },
      { header: "Receita", key: "receita", width: 14 },
      { header: "Ticket Médio", key: "ticket_medio", width: 16 },
      { header: "Tempo Médio", key: "tempo_medio", width: 14 },
    ];
    (data.lojas_top || []).forEach((r) => ws1.addRow(r));

    const ws2 = wb.addWorksheet(`Canais ${period}`);
    ws2.columns = [
      { header: "Canal", key: "saleschannel", width: 20 },
      { header: "Pedidos", key: "pedidos", width: 12 },
      { header: "Receita", key: "receita", width: 14 },
      { header: "Ticket Médio", key: "ticket_medio", width: 16 },
    ];
    (data.canais_venda || []).forEach((r) => ws2.addRow(r));
  }

  res.setHeader(
    "Content-Type",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
  );
  res.setHeader("Content-Disposition", 'attachment; filename="relatorio_cannoli.xlsx"');
  await wb.xlsx.write(res);
  res.end();
}

/* ========== PDF ========== */
async function generatePDF(datasets, res) {
  const doc = new PDFDocument({ margin: 40 });
  res.setHeader("Content-Type", "application/pdf");
  res.setHeader("Content-Disposition", 'attachment; filename="relatorio_cannoli.pdf"');
  doc.pipe(res);

  doc.fontSize(18).text("📊 Relatório Consolidado Cannoli", { align: "center" }).moveDown();

  for (const [period, data] of Object.entries(datasets)) {
    if (!data) continue;

    doc.fontSize(14).fillColor("#FF8C00").text(`🔸 Período: ${period}`, { underline: true }).moveDown(0.5);

    const resumo = data?.resumo_geral || {};
    doc
      .fontSize(12)
      .fillColor("black")
      .text(`Ticket médio: R$ ${resumo.ticket_medio_geral ?? 0}`)
      .text(`Tempo médio de preparo: ${resumo.tempo_medio_preparo ?? 0} min`)
      .moveDown(0.5)
      .text("Top Lojas:", { bold: true });

    (data.lojas_top || []).slice(0, 10).forEach((l, i) =>
      doc.text(`${i + 1}. ${l["store.name"]} — R$ ${Number(l.receita).toFixed(2)}`, { indent: 10 })
    );

    doc.moveDown(1);
  }

  doc.end();
}
