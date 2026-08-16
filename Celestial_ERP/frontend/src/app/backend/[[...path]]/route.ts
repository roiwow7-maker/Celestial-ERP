import type { NextRequest } from "next/server";

export const dynamic = "force-dynamic";
export const runtime = "nodejs";

const backendBase = (process.env.DJANGO_BACKEND_URL ?? "http://127.0.0.1:8000").replace(/\/$/, "");
const proxyPrefix = "/backend";
const hopByHopHeaders = new Set([
  "connection",
  "content-length",
  "content-encoding",
  "keep-alive",
  "proxy-authenticate",
  "proxy-authorization",
  "te",
  "trailer",
  "transfer-encoding",
  "upgrade",
]);

type RouteParameters = { params: Promise<{ path?: string[] }> };

function rewriteLocation(location: string): string {
  if (location.startsWith(backendBase)) return `${proxyPrefix}${location.slice(backendBase.length) || "/"}`;
  if (location.startsWith("/") && !location.startsWith("//")) return `${proxyPrefix}${location}`;
  return location;
}

function rewriteText(content: string): string {
  const escapedBackend = backendBase.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  return content
    .replace(new RegExp(escapedBackend, "g"), proxyPrefix)
    .replace(/(["'(=])\/(?!\/|backend(?:\/|["']))/g, `$1${proxyPrefix}/`);
}

async function proxy(request: NextRequest, context: RouteParameters) {
  await context.params;
  const proxiedPath = request.nextUrl.pathname.slice(proxyPrefix.length) || "/";
  const target = new URL(proxiedPath, `${backendBase}/`);
  target.search = request.nextUrl.search;

  const headers = new Headers(request.headers);
  headers.delete("content-length");
  headers.delete("accept-encoding");
  headers.set("host", target.host);
  if (headers.has("origin")) headers.set("origin", backendBase);
  if (headers.has("referer")) headers.set("referer", `${backendBase}/`);

  let upstream: Response;
  try {
    upstream = await fetch(target, {
      method: request.method,
      headers,
      body: request.method === "GET" || request.method === "HEAD" ? undefined : await request.arrayBuffer(),
      redirect: "manual",
      cache: "no-store",
    });
  } catch (error) {
    const detail = error instanceof Error ? error.message : "Error desconocido";
    return new Response(
      `<!doctype html><html lang="es"><meta charset="utf-8"><style>body{font:16px system-ui;background:#f8fafc;color:#172033;padding:48px}main{max-width:720px;margin:auto;background:white;padding:32px;border-radius:16px;box-shadow:0 15px 50px #0f172a18}code{background:#eef2ff;padding:3px 7px;border-radius:6px}</style><main><h1>Django no está disponible</h1><p>Inicia el backend en <code>${backendBase}</code> y vuelve a cargar esta vista.</p><p>${detail}</p></main></html>`,
      { status: 502, headers: { "content-type": "text/html; charset=utf-8" } },
    );
  }

  const responseHeaders = new Headers();
  upstream.headers.forEach((value, key) => {
    if (!hopByHopHeaders.has(key.toLowerCase()) && key.toLowerCase() !== "set-cookie") {
      responseHeaders.append(key, value);
    }
  });
  responseHeaders.delete("x-frame-options");
  responseHeaders.delete("content-security-policy");

  const location = upstream.headers.get("location");
  if (location) responseHeaders.set("location", rewriteLocation(location));

  const getSetCookie = (upstream.headers as Headers & { getSetCookie?: () => string[] }).getSetCookie;
  const cookies = getSetCookie ? getSetCookie.call(upstream.headers) : [];
  for (const cookie of cookies) responseHeaders.append("set-cookie", cookie);

  const contentType = upstream.headers.get("content-type") ?? "";
  if (contentType.includes("text/html") || contentType.includes("text/css") || contentType.includes("javascript")) {
    return new Response(rewriteText(await upstream.text()), {
      status: upstream.status,
      headers: responseHeaders,
    });
  }

  return new Response(upstream.body, { status: upstream.status, headers: responseHeaders });
}

export const GET = proxy;
export const POST = proxy;
export const PUT = proxy;
export const PATCH = proxy;
export const DELETE = proxy;
export const HEAD = proxy;
export const OPTIONS = proxy;
