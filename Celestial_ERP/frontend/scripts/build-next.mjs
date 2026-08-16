import { spawn } from "node:child_process";
import path from "node:path";

const nextCli = path.join(process.cwd(), "node_modules", "next", "dist", "bin", "next");
const build = spawn(process.execPath, [nextCli, "build", "--webpack"], {
  cwd: process.cwd(),
  env: { ...process.env, NEXT_DIST_DIR: ".next-build" },
  stdio: "inherit",
});

build.on("exit", (code) => process.exit(code ?? 1));
