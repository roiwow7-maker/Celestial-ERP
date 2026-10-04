import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: "standalone",
  distDir: process.env.NEXT_DIST_DIR ?? ".next",
  // Node 24 does not flush `tsc --showConfig` when Next captures the CLI output
  // through a pipe. The compiler API performs the same build-time validation.
  experimental: { useTypeScriptCli: false },
  allowedDevOrigins: ["127.0.0.1", "localhost", "192.168.50.*"],
  skipTrailingSlashRedirect: true,
};

export default nextConfig;
