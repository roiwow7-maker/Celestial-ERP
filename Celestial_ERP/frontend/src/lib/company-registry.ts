import { readFileSync, existsSync } from "node:fs";

import { resolve } from "node:path";

export type Company = { id: string; name: string; backend: string; domains: string[]; modules: string[] };

export function companyRegistry(): Company[] {
  const local = resolve(process.cwd(), "../../config/companies.json");
  const file = process.env.ERP_COMPANIES_FILE ?? (existsSync(local) ? local : undefined);
  const raw: unknown = file ? JSON.parse(readFileSync(file, "utf8")) : [
    { id: "default", name: "Empresa actual", backend: process.env.DJANGO_BACKEND_URL ?? "http://127.0.0.1:8000", domains: [], modules: ["payroll", "attendance", "accounting", "inventory", "commerce"] },
  ];
  if (!Array.isArray(raw) || raw.length === 0) throw new Error("Registro de empresas inválido");
  const ids = new Set<string>();
  const backends = new Set<string>();
  return raw.map((value) => {
    if (!value || typeof value.id !== "string" || !/^[a-z][a-z0-9_-]{0,39}$/.test(value.id) || typeof value.name !== "string" || !value.name.trim() || typeof value.backend !== "string") throw new Error("Empresa inválida");
    const url = new URL(value.backend);
    if (!["http:", "https:"].includes(url.protocol) || url.username || url.password || url.pathname !== "/" || url.search || url.hash) throw new Error("Backend inválido");
    if (ids.has(value.id) || backends.has(url.origin)) throw new Error("Las empresas deben usar identificadores y backends distintos");
    ids.add(value.id); backends.add(url.origin);
    const rawDomains: unknown[] = Array.isArray(value.domains) ? value.domains : [];
    const rawModules: unknown[] = Array.isArray(value.modules) ? value.modules : [];
    const domains = rawDomains.filter((domain): domain is string => typeof domain === "string").map((domain: string) => domain.toLowerCase().replace(/^@/, "").trim());
    const modules = rawModules.filter((module): module is string => typeof module === "string");
    return { id: value.id, name: value.name.trim(), backend: url.origin, domains, modules };
  });
}
