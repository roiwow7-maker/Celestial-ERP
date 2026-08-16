const { app, BrowserWindow, dialog, utilityProcess } = require("electron");
const path = require("node:path");

const isDevelopment = !app.isPackaged;
const frontendUrl = "http://127.0.0.1:3000";
let nextServer;

function createWindow() {
  const window = new BrowserWindow({
    width: 1440,
    height: 900,
    minWidth: 1024,
    minHeight: 700,
    show: false,
    webPreferences: {
      preload: path.join(__dirname, "preload.cjs"),
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: true,
    },
  });

  window.once("ready-to-show", () => window.show());
  window.loadURL(frontendUrl);
}

async function waitForFrontend(maxAttempts = 80) {
  for (let attempt = 0; attempt < maxAttempts; attempt += 1) {
    try {
      const response = await fetch(frontendUrl);
      if (response.ok) return;
    } catch {
      // El servidor todavia esta iniciando.
    }
    await new Promise((resolve) => setTimeout(resolve, 250));
  }
  throw new Error("El frontend no respondio a tiempo.");
}

async function startProductionServer() {
  const serverPath = path.join(process.resourcesPath, "app", "server.js");
  nextServer = utilityProcess.fork(serverPath, [], {
    env: {
      ...process.env,
      HOSTNAME: "127.0.0.1",
      PORT: "3000",
      NODE_ENV: "production",
      NODE_PATH: path.join(process.resourcesPath, "app", "vendor_modules"),
    },
    stdio: "pipe",
  });

  nextServer.stdout?.on("data", (data) => console.log(data.toString().trim()));
  nextServer.stderr?.on("data", (data) => console.error(data.toString().trim()));
  await waitForFrontend();
}

app.whenReady().then(async () => {
  try {
    if (!isDevelopment) await startProductionServer();
    createWindow();
  } catch (error) {
    dialog.showErrorBox("Celestial ERP", String(error));
    app.quit();
  }
});

app.on("window-all-closed", () => {
  if (process.platform !== "darwin") app.quit();
});

app.on("before-quit", () => nextServer?.kill());

app.on("activate", () => {
  if (BrowserWindow.getAllWindows().length === 0) createWindow();
});
