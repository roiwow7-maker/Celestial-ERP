import type { NextRequest } from "next/server";
import { companyRegistry } from "@/lib/company-registry";

export const dynamic = "force-dynamic";
export const runtime = "nodejs";
type RouteParameters = { params: Promise<{ path?: string[] }> };
const skipped = new Set(["connection", "content-length", "content-encoding", "keep-alive", "proxy-authenticate", "proxy-authorization", "te", "trailer", "transfer-encoding", "upgrade", "set-cookie"]);
const maxBody = 27 * 1024 * 1024;

async function readBody(request: NextRequest) {
  if (!request.body) return undefined;
  const reader = request.body.getReader();
  const chunks: Uint8Array[] = []; let size = 0;
  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    size += value.length;
    if (size > maxBody) { await reader.cancel(); throw new Error("BODY_TOO_LARGE"); }
    chunks.push(value);
  }
  return Buffer.concat(chunks);
}

async function proxy(request: NextRequest, context: RouteParameters) {
  const { path = [] } = await context.params;
  const companies = companyRegistry();
  const scoped = path[0] === "company";
  const company = companies.find((item) => item.id === (scoped ? path[1] : "default"));
  if (!company) return Response.json({ error: "Empresa no disponible." }, { status: 404 });
  const parts = scoped ? path.slice(2) : path;
  if (parts.some((part) => /[\\/]/.test(part) || part === "." || part === "..")) return new Response(null, { status: 400 });
  const prefix = scoped ? `/backend/company/${company.id}` : "/backend";
  const cookiePrefix = scoped ? `erp_${company.id}_` : "";
  const target = new URL("/" + parts.map(encodeURIComponent).join("/") + (parts.length && request.nextUrl.pathname.endsWith("/") ? "/" : ""), company.backend);
  target.search = request.nextUrl.search;
  const safe = ["GET", "HEAD", "OPTIONS"].includes(request.method);
  // Verificar el origen ANTES de traducirlo para Django.
  if (!safe) {
    const origin = request.headers.get("origin");
    const allowedOrigins = process.env.ERP_PUBLIC_ORIGIN ? [process.env.ERP_PUBLIC_ORIGIN] : ["http://127.0.0.1:3000", "http://localhost:3000"];
    if (!origin || !allowedOrigins.includes(origin) || request.headers.get("sec-fetch-site") === "cross-site") {
      return Response.json({ error: "Origen de solicitud no permitido." }, { status: 403 });
    }
  }
  const headers = new Headers(request.headers);
  for (const key of [...headers.keys()]) {
    if (skipped.has(key.toLowerCase()) || key.toLowerCase().startsWith("x-forwarded-") || ["forwarded", "authorization", "x-erp-company"].includes(key.toLowerCase())) headers.delete(key);
  }
  headers.delete("accept-encoding");
  const cookies = (request.headers.get("cookie") ?? "").split(";").map((part) => part.trim()).filter(Boolean);
  const selectedCookies = ["sessionid", "csrftoken"].flatMap((name) => {
    const scopedCookie = cookies.find((part) => part.startsWith(`${cookiePrefix}${name}=`));
    if (scopedCookie) return [scoped ? scopedCookie.slice(cookiePrefix.length) : scopedCookie];
    // Migrar únicamente la sesión histórica de default; nunca enviarla a otra empresa.
    const legacy = company.id === "default" ? cookies.find((part) => part.startsWith(`${name}=`)) : undefined;
    return legacy ? [legacy] : [];
  });
  headers.set("cookie", selectedCookies.join("; "));
  headers.set("host", target.host);
  headers.set("x-forwarded-proto", request.nextUrl.protocol.slice(0, -1));
  if (headers.has("origin")) headers.set("origin", company.backend);
  if (headers.has("referer")) headers.set("referer", `${company.backend}/`);
  let upstream: Response;
  try {
    upstream = await fetch(target, { method: request.method, headers, body: safe ? undefined : await readBody(request), redirect: "manual", cache: "no-store", signal: AbortSignal.timeout(60000) });
  } catch (error) {
    const large = error instanceof Error && error.message === "BODY_TOO_LARGE";
    return Response.json({ error: large ? "El archivo supera el tamaño permitido." : "El servicio de esta empresa no está disponible." }, { status: large ? 413 : 502 });
  }
  if (upstream.headers.get("x-erp-company") !== company.id) return Response.json({ error: "La identidad del servicio no coincide con la empresa seleccionada." }, { status: 502 });
  const output = new Headers();
  upstream.headers.forEach((value, key) => { if (!skipped.has(key.toLowerCase())) output.append(key, value); });
  output.set("Cache-Control", "no-store, private");
  const rewriteLocation = (location: string) => {
    if (location.startsWith(company.backend + "/")) return prefix + location.slice(company.backend.length);
    if (location.startsWith("/") && !location.startsWith("//")) return prefix + location;
    return location;
  };
  const location = upstream.headers.get("location");
  if (location) output.set("location", rewriteLocation(location));
  for (const cookie of upstream.headers.getSetCookie()) {
    // Nombre por empresa; Path=/ permite que React lea exclusivamente su token CSRF.
    output.append("set-cookie", cookiePrefix + cookie.replace(/;\s*Domain=[^;]*/ig, "").replace(/;\s*Path=[^;]*/ig, "; Path=/"));
  }
  const contentType = upstream.headers.get("content-type") ?? "";
  if (/text\/html|text\/css|javascript/.test(contentType)) {
    const content = (await upstream.text()).replaceAll(company.backend + "/", prefix + "/").replace(/(["'(=])\/(?!\/|backend(?:\/|["']))/g, `$1${prefix}/`);
    return new Response(content, { status: upstream.status, headers: output });
  }
  return new Response(upstream.body, { status: upstream.status, headers: output });
}
export const GET = proxy;
export const POST = proxy;
export const PUT = proxy;
export const PATCH = proxy;
export const DELETE = proxy;
export const HEAD = proxy;
export const OPTIONS = proxy;
