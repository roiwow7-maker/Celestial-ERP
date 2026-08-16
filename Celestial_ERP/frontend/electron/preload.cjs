const { contextBridge } = require("electron");

contextBridge.exposeInMainWorld("celestialDesktop", {
  platform: process.platform,
});
