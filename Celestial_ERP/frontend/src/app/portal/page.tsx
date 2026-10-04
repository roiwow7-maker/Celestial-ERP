import type { Metadata } from "next";
import { redirect } from "next/navigation";
import { ErpShell } from "@/components/erp-shell";
import { companyRegistry } from "@/lib/company-registry";

export const dynamic = "force-dynamic";
export const metadata: Metadata = { title: "Mi empresa | Celestial ERP", robots: { index: false, follow: false } };

export default async function PortalPage({ searchParams }: { searchParams: Promise<{ company?: string | string[] }> }) {
  const params = await searchParams;
  const company = companyRegistry().find(item => item.id === params.company);
  if (!company) redirect("/login");
  return <ErpShell key={company.id} company={{ id: company.id, name: company.name }} />;
}
