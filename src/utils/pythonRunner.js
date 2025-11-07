import { spawn } from "child_process";

export function runPythonScript(scriptPath, args = []) {
  return new Promise((resolve, reject) => {
    const py = spawn("python", [scriptPath, ...args], {
      cwd: process.cwd(),
      env: { ...process.env, PYTHONIOENCODING: "utf-8" },
    });

    let output = "", error = "";

    py.stdout.on("data", (chunk) => (output += chunk.toString("utf-8")));
    py.stderr.on("data", (chunk) => (error += chunk.toString("utf-8")));

    py.on("close", (code) => {
      if (code !== 0) reject(error || "Erro Python");
      else resolve(output.trim());
    });
  });
}
