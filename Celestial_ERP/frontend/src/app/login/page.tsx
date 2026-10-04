import type { Metadata } from "next";
import { redirect } from "next/navigation";
import { LoginPortal } from "@/components/login-portal";
import { PublicNavbar } from "@/components/public-navbar";
import { companyRegistry } from "@/lib/company-registry";

export const dynamic = "force-dynamic";
export const metadata: Metadata = { title: "Iniciar sesión | Celestial ERP" };

export default async function LoginPage({ searchParams }: { searchParams: Promise<{ company?: string | string[] }> }) {
  const { company } = await searchParams;
  const companies = companyRegistry().map(({ id, name, domains }) => ({ id, name, domains }));
  if (company !== undefined && (typeof company !== "string" || !companies.some(item => item.id === company))) redirect("/login");
  return <><PublicNavbar /><LoginPortal companies={companies} initialCompany={typeof company === "string" ? company : undefined} /></>;
}
