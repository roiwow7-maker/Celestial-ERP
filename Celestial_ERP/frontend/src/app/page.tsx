import { CompanyEntry } from "@/components/company-entry";
import { redirect } from "next/navigation";

export default async function Home({ searchParams }: { searchParams: Promise<{ company?: string | string[] }> }) {
  const { company } = await searchParams;
  // Preserve bookmarks created before the portal received its own route.
  if (typeof company === "string") redirect(`/portal?company=${encodeURIComponent(company)}`);
  return <CompanyEntry />;
}
