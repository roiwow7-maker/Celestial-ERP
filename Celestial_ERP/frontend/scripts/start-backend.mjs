import { spawn } from "node:child_process";
import { access } from "node:fs/promises";
import path from "node:path";

const backendUrl = process.env.DJANGO_BACKEND_URL ?? "http://127.0.0.1:8000";

let backendIsRunning = false;
try {
  const response = await fetch(`${backendUrl}/login/`);
  if (response.ok) {
    console.log(`Django ya está activo en ${backendUrl}`);
    backendIsRunning = true;
  }
} catch {
  // Django no está activo; se inicia debajo.
}

if (backendIsRunning) {
  setInterval(() => {}, 2_147_483_647);
} else {
  const projectRoot = path.resolve(process.cwd(), "..", "..");
  const djangoRoot = path.join(projectRoot, "Celestial_ERP");
  const virtualPython = process.platform === "win32"
    ? path.join(projectRoot, "venv", "Scripts", "python.exe")
    : path.join(projectRoot, "venv", "bin", "python");

  let python = process.platform === "win32" ? "python" : "python3";
  try {
    await access(virtualPython);
    python = virtualPython;
  } catch {
    console.warn("No se encontró el entorno virtual; se usará el Python del sistema.");
  }

  const django = spawn(python, ["manage.py", "runserver", "127.0.0.1:8000"], {
    cwd: djangoRoot,
    env: {
      ...process.env,
      ERP_SETTINGS_ENV: process.env.ERP_SETTINGS_ENV ?? "dev",
      DJANGO_ALLOWED_HOSTS: process.env.DJANGO_ALLOWED_HOSTS ?? "127.0.0.1,localhost",
      DJANGO_DEBUG: process.env.DJANGO_DEBUG ?? "true",
    },
    stdio: "inherit",
  });

  for (const signal of ["SIGINT", "SIGTERM"]) {
    process.on(signal, () => django.kill(signal));
  }

  django.on("exit", (code) => process.exit(code ?? 0));
}
