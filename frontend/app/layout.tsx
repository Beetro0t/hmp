import "../styles/globals.css";

export const metadata = {
  title: "Central Coast Housing Market Wizard",
  description: "Tiered valuation ranges for Central Coast, NSW."
};

export default function RootLayout({
  children
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <div className="min-h-screen bg-slate-50">
          <header className="border-b border-slate-200 bg-white">
            <div className="mx-auto flex max-w-5xl items-center justify-between px-6 py-4">
              <div>
                <h1 className="text-lg font-semibold">
                  Central Coast Housing Market Wizard
                </h1>
                <p className="text-sm text-slate-500">
                  Central Coast, NSW — Tiered valuation ranges with uncertainty
                </p>
              </div>
              <nav className="flex gap-4 text-sm text-slate-600">
                <a href="/" className="hover:text-slate-900">
                  Wizard
                </a>
                <a href="/metrics" className="hover:text-slate-900">
                  Model metrics
                </a>
              </nav>
            </div>
          </header>
          <main className="mx-auto max-w-5xl px-6 py-8">{children}</main>
        </div>
      </body>
    </html>
  );
}
