import { Sidebar } from "@/components/layout/Sidebar";

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="min-h-screen bg-background">
      <div className="pointer-events-none fixed inset-0 bg-gradient-radial" />
      <Sidebar />
      <main className="relative ml-64 min-h-screen p-8">{children}</main>
    </div>
  );
}
