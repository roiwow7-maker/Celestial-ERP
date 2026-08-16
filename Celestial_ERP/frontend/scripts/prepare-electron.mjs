import { cp, mkdir } from "node:fs/promises";
import path from "node:path";

const root = process.cwd();
const buildDir = path.join(root, ".next-build");
const standalone = path.join(buildDir, "standalone");

await mkdir(path.join(standalone, ".next-build"), { recursive: true });
await cp(path.join(buildDir, "static"), path.join(standalone, ".next-build", "static"), {
  recursive: true,
  force: true,
});
await cp(path.join(root, "public"), path.join(standalone, "public"), {
  recursive: true,
  force: true,
});
await cp(path.join(standalone, "node_modules"), path.join(standalone, "vendor_modules"), {
  recursive: true,
  force: true,
});
