import { companyRegistry } from "@/lib/company-registry";
export const dynamic = "force-dynamic";
export function GET() {
  return Response.json({ companies: companyRegistry().map(({ id, name, domains, modules }) => ({ id, name, domains, modules })) }, { headers: { "Cache-Control": "no-store" } });
}
