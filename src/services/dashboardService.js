import { spawn } from "child_process";
import path from "path";
import { fileURLToPath } from "url";

// Resolve corretamente __dirname e __filename em módulos ES
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

/**
 * Executa um script Python e retorna o JSON resultante.
 *
 * @param {"admin"|"client"} userRole - Define qual script Python rodar.
 * @param {"30d"|"60d"|"90d"} period - Período desejado.
 * @returns {Promise<object>} JSON retornado pelo script Python.
 */
export async function getInsights(period = "30d", userRole = "client") {
  return new Promise((resolve, reject) => {
    // Seleciona o script conforme o tipo de usuário
    const script = userRole === "admin" ? "insights_admin.py" : "insights_from_json.py";
    const scriptPath = path.resolve(__dirname, `../python/${script}`);

    console.log(`🧠 Executando script Python (${userRole}) → ${scriptPath}`);

    // ⚙️ Executa o Python sem sobrescrever o objeto global "process"
    const pythonProcess = spawn("python", [scriptPath, period], {
      cwd: path.resolve(__dirname, "../python"),
      env: { ...process.env, PYTHONIOENCODING: "utf-8" },
    });

    // Buffers para capturar saída e erros
    let stdout = "";
    let stderr = "";

    pythonProcess.stdout.on("data", (chunk) => {
      stdout += chunk.toString();
    });

    pythonProcess.stderr.on("data", (chunk) => {
      stderr += chunk.toString();
    });

    // Evento disparado ao encerrar o processo Python
    pythonProcess.on("close", (code) => {
      if (code !== 0 || stderr) {
        console.error("❌ Erro ao executar Python:", stderr);
        return reject(new Error(stderr || "Falha ao gerar insights."));
      }

      try {
        const clean = stdout.trim();
        const jsonMatch = clean.match(/\{[\s\S]*\}$/);

        if (!jsonMatch) throw new Error("Nenhum JSON encontrado na saída do Python.");

        const data = JSON.parse(jsonMatch[0]);
        console.log(`✅ Insight ${userRole} (${period}) recebido com sucesso!`);
        resolve(data);
      } catch (err) {
        console.error("⚠️ Erro ao parsear JSON:", err.message);
        console.log("🪵 Saída completa:", stdout);
        reject(err);
      }
    });
  });
}
