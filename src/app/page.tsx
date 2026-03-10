import Link from "next/link";
import { Button } from "@/components/ui/button";

export default function HomePage() {
  return (
    <div className="relative">
      {/* Hero Section */}
      <section className="relative overflow-hidden">
        {/* Background effects */}
        <div className="absolute inset-0 -z-10">
          <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-primary/8 rounded-full blur-3xl" />
          <div className="absolute bottom-1/4 right-1/4 w-80 h-80 bg-chart-2/8 rounded-full blur-3xl" />
          <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-primary/20 to-transparent" />
        </div>

        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 pt-24 pb-20">
          <div className="text-center max-w-4xl mx-auto">
            <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full border border-primary/20 bg-primary/5 text-sm text-primary mb-8 animate-fade-in-up">
              <span className="w-2 h-2 rounded-full bg-primary animate-pulse" />
              Exhibition Intelligence Platform
            </div>

            <h1 className="text-4xl sm:text-5xl lg:text-7xl font-bold tracking-tight leading-[1.1] mb-6 animate-fade-in-up" style={{ animationDelay: "0.1s" }}>
              Extract{" "}
              <span className="gradient-text">Exhibition Data</span>
              <br />
              Like Never Before
            </h1>

            <p className="text-lg sm:text-xl text-muted-foreground max-w-2xl mx-auto mb-10 leading-relaxed animate-fade-in-up" style={{ animationDelay: "0.2s" }}>
              Turn floor plans into structured booth data. Scrape exhibitor directories into clean databases.
              Built for exhibition professionals who need real intelligence, fast.
            </p>

            <div className="flex flex-col sm:flex-row items-center justify-center gap-4 animate-fade-in-up" style={{ animationDelay: "0.3s" }}>
              <Link href="/dashboard">
                <Button size="lg" className="bg-primary hover:bg-primary/90 text-primary-foreground shadow-lg shadow-primary/25 px-8 text-base">
                  Start Extracting →
                </Button>
              </Link>
              <Link href="/about">
                <Button variant="outline" size="lg" className="px-8 text-base border-border/60 hover:bg-accent/50">
                  Learn More
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Tools Section */}
      <section className="py-24 relative">
        <div className="absolute inset-0 -z-10 bg-gradient-to-b from-transparent via-primary/3 to-transparent" />
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl sm:text-4xl font-bold mb-4">Two Powerful Tools</h2>
            <p className="text-muted-foreground text-lg max-w-2xl mx-auto">
              Everything you need to extract and organize exhibition data from any source.
            </p>
          </div>

          <div className="grid md:grid-cols-2 gap-6 lg:gap-8">
            {/* Floor Plan Tool */}
            <div className="glass-card rounded-2xl p-8 hover:border-primary/30 transition-all duration-300 group">
              <div className="w-14 h-14 rounded-xl bg-primary/10 border border-primary/20 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" className="text-primary">
                  <rect x="2" y="2" width="20" height="20" rx="2" />
                  <path d="M2 8h20" />
                  <path d="M8 2v20" />
                  <path d="M14 8v6" />
                  <path d="M8 14h6" />
                </svg>
              </div>
              <h3 className="text-xl font-semibold mb-3">Floor Plan OCR Extractor</h3>
              <p className="text-muted-foreground leading-relaxed mb-6">
                Upload PDF or image floor plans and extract booth numbers, sizes, exhibitor names, hall info, and more using OCR and smart pattern recognition.
              </p>
              <div className="flex flex-wrap gap-2 mb-6">
                {["PDF", "PNG", "JPG", "OCR", "Regex"].map((tag) => (
                  <span key={tag} className="px-2.5 py-1 text-xs rounded-md bg-primary/10 text-primary border border-primary/15">
                    {tag}
                  </span>
                ))}
              </div>
              <Link href="/dashboard/floorplan">
                <Button variant="outline" className="border-primary/30 hover:bg-primary/10 text-primary">
                  Open Tool →
                </Button>
              </Link>
            </div>

            {/* Scraper Tool */}
            <div className="glass-card rounded-2xl p-8 hover:border-chart-2/30 transition-all duration-300 group">
              <div className="w-14 h-14 rounded-xl bg-chart-2/10 border border-chart-2/20 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" className="text-chart-2">
                  <circle cx="12" cy="12" r="10" />
                  <path d="M2 12h20" />
                  <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z" />
                </svg>
              </div>
              <h3 className="text-xl font-semibold mb-3">Exhibitor Web Scraper</h3>
              <p className="text-muted-foreground leading-relaxed mb-6">
                Paste any exhibitor directory URL and scrape company names, booth numbers, contacts, social links, and more — with auto-pagination and detail page traversal.
              </p>
              <div className="flex flex-wrap gap-2 mb-6">
                {["Auto-Pagination", "Detail Pages", "LinkedIn", "Contacts", "JS Support"].map((tag) => (
                  <span key={tag} className="px-2.5 py-1 text-xs rounded-md bg-chart-2/10 text-chart-2 border border-chart-2/15">
                    {tag}
                  </span>
                ))}
              </div>
              <Link href="/dashboard/scraper">
                <Button variant="outline" className="border-chart-2/30 hover:bg-chart-2/10 text-chart-2">
                  Open Tool →
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section className="py-24">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl sm:text-4xl font-bold mb-4">How It Works</h2>
            <p className="text-muted-foreground text-lg max-w-2xl mx-auto">
              From raw exhibition data to structured intelligence in three simple steps.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {[
              {
                step: "01",
                title: "Upload or Paste",
                description: "Upload a floor plan file (PDF, PNG, JPG) or paste an exhibitor directory URL.",
                icon: (
                  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                    <polyline points="17 8 12 3 7 8" />
                    <line x1="12" y1="3" x2="12" y2="15" />
                  </svg>
                ),
              },
              {
                step: "02",
                title: "Process & Extract",
                description: "Our engine handles OCR, parsing, scraping, pagination, and detail page traversal automatically.",
                icon: (
                  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M12 2v4" />
                    <path d="M12 18v4" />
                    <path d="M4.93 4.93l2.83 2.83" />
                    <path d="M16.24 16.24l2.83 2.83" />
                    <path d="M2 12h4" />
                    <path d="M18 12h4" />
                    <path d="M4.93 19.07l2.83-2.83" />
                    <path d="M16.24 7.76l2.83-2.83" />
                  </svg>
                ),
              },
              {
                step: "03",
                title: "Export & Use",
                description: "Download clean CSV, Excel, or JSON files. Use the data for sales, logistics, or marketing.",
                icon: (
                  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                    <polyline points="7 10 12 15 17 10" />
                    <line x1="12" y1="15" x2="12" y2="3" />
                  </svg>
                ),
              },
            ].map((item) => (
              <div key={item.step} className="relative text-center p-8">
                <div className="text-6xl font-bold text-primary/10 mb-4">{item.step}</div>
                <div className="w-12 h-12 rounded-full bg-primary/10 border border-primary/20 flex items-center justify-center mx-auto mb-5 text-primary">
                  {item.icon}
                </div>
                <h3 className="text-lg font-semibold mb-2">{item.title}</h3>
                <p className="text-muted-foreground text-sm leading-relaxed">{item.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Who This Is For */}
      <section className="py-24 relative">
        <div className="absolute inset-0 -z-10 bg-gradient-to-b from-transparent via-chart-2/3 to-transparent" />
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl sm:text-4xl font-bold mb-4">Built for Exhibition Professionals</h2>
            <p className="text-muted-foreground text-lg max-w-2xl mx-auto">
              Whether you build stands, coordinate logistics, or sell exhibition space — this platform saves you hours.
            </p>
          </div>

          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {[
              { title: "Stand Builders", desc: "Extract booth dimensions and layouts from floor plans instantly." },
              { title: "Marketing Agencies", desc: "Build exhibitor contact lists from any directory in minutes." },
              { title: "Logistics Teams", desc: "Get structured hall and booth data for planning shipments." },
              { title: "Sales Teams", desc: "Identify new leads with full company details and contacts." },
            ].map((item) => (
              <div key={item.title} className="glass-card rounded-xl p-6 hover:border-primary/20 transition-colors">
                <h4 className="font-semibold mb-2">{item.title}</h4>
                <p className="text-sm text-muted-foreground leading-relaxed">{item.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Export Section */}
      <section className="py-24">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="glass-card rounded-2xl p-10 lg:p-16 text-center">
            <h2 className="text-3xl sm:text-4xl font-bold mb-4">Export in Any Format</h2>
            <p className="text-muted-foreground text-lg max-w-2xl mx-auto mb-10">
              Download your extracted data instantly in the format you need for your workflow.
            </p>
            <div className="flex flex-wrap items-center justify-center gap-6">
              {[
                { format: "CSV", desc: "Spreadsheet ready" },
                { format: "Excel", desc: "Rich formatted tables" },
                { format: "JSON", desc: "API & developer ready" },
              ].map((item) => (
                <div key={item.format} className="flex items-center gap-3 px-6 py-4 rounded-xl bg-card border border-border/50">
                  <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center text-primary font-bold text-sm">
                    {item.format}
                  </div>
                  <div className="text-left">
                    <div className="text-sm font-semibold">{item.format}</div>
                    <div className="text-xs text-muted-foreground">{item.desc}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-24">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl sm:text-4xl font-bold mb-4">
            Ready to Extract{" "}
            <span className="gradient-text">Exhibition Intelligence</span>?
          </h2>
          <p className="text-muted-foreground text-lg max-w-xl mx-auto mb-8">
            Start extracting booth data and exhibitor contacts now. No sign-up required for the local MVP.
          </p>
          <Link href="/dashboard">
            <Button size="lg" className="bg-primary hover:bg-primary/90 text-primary-foreground shadow-lg shadow-primary/25 px-10 text-base animate-pulse-glow">
              Open the App →
            </Button>
          </Link>
        </div>
      </section>
    </div>
  );
}
