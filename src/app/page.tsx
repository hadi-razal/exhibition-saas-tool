import Link from "next/link";
import { Button } from "@/components/ui/button";

export default function HomePage() {
  return (
    <div className="relative">
      {/* ── Hero ─────────────────────────────────────────────────────── */}
      <section className="relative overflow-hidden hero-bg dot-grid">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 pt-28 pb-24">
          <div className="text-center max-w-3xl mx-auto">
            {/* Badge */}
            <div
              className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full border border-primary/20 bg-primary/6 text-xs font-semibold text-primary mb-8 animate-fade-in-up"
            >
              <span className="w-1.5 h-1.5 rounded-full bg-primary" />
              Exhibition Intelligence Platform
            </div>

            <h1
              className="text-4xl sm:text-5xl lg:text-[3.75rem] font-bold tracking-tight leading-[1.1] mb-6 animate-fade-in-up text-foreground"
              style={{ animationDelay: "0.08s" }}
            >
              Turn Floor Plans Into{" "}
              <span className="gradient-text">Structured Data</span>
            </h1>

            <p
              className="text-base sm:text-lg text-muted-foreground max-w-2xl mx-auto mb-10 leading-relaxed animate-fade-in-up"
              style={{ animationDelay: "0.16s" }}
            >
              Upload any exhibition floor plan and extract every booth number,
              exhibitor name, dimensions, and area automatically.
              No API key. No cloud. Just Python.
            </p>

            <div
              className="flex flex-col sm:flex-row items-center justify-center gap-3 animate-fade-in-up"
              style={{ animationDelay: "0.24s" }}
            >
              <Link href="/dashboard">
                <Button
                  size="lg"
                  className="bg-primary hover:bg-primary/90 text-primary-foreground shadow-md shadow-primary/20 px-8 font-semibold animate-pulse-ring"
                >
                  Start Extracting →
                </Button>
              </Link>
              <Link href="/about">
                <Button variant="outline" size="lg" className="px-8 border-border hover:bg-accent font-medium">
                  Learn More
                </Button>
              </Link>
            </div>
          </div>

          {/* Feature pill strip */}
          <div
            className="flex flex-wrap items-center justify-center gap-2 mt-12 animate-fade-in-up"
            style={{ animationDelay: "0.32s" }}
          >
            {[
              "Booth Numbers", "Exhibitor Names", "Dimensions (m)",
              "Area (m²)", "Hall Info", "Filters Facilities",
              "Booth-Only Rows", "CSV · Excel · JSON",
            ].map((feat) => (
              <span key={feat} className="tag-neutral text-xs px-3 py-1 rounded-full font-medium">
                {feat}
              </span>
            ))}
          </div>
        </div>
      </section>

      {/* ── Divider ──────────────────────────────────────────────────── */}
      <div className="divider mx-auto max-w-5xl" />

      {/* ── Tools Section ────────────────────────────────────────────── */}
      <section className="py-24 bg-white">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-14">
            <h2 className="text-3xl sm:text-4xl font-bold tracking-tight mb-3">Two Powerful Tools</h2>
            <p className="text-muted-foreground max-w-xl mx-auto">
              Extract exhibition data from any source — floor plans or exhibitor directories.
            </p>
          </div>

          <div className="grid md:grid-cols-2 gap-6">
            {/* Floor Plan Card */}
            <div className="card-elevated rounded-2xl p-8 group hover:shadow-lg hover:shadow-primary/8 transition-all duration-300">
              <div className="flex items-start gap-4 mb-5">
                <div className="w-12 h-12 rounded-xl bg-primary/8 border border-primary/15 flex items-center justify-center flex-shrink-0 group-hover:scale-105 transition-transform">
                  <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" className="text-primary">
                    <rect x="2" y="2" width="20" height="20" rx="2" />
                    <path d="M2 8h20" />
                    <path d="M8 2v20" />
                  </svg>
                </div>
                <div>
                  <h3 className="text-lg font-bold text-foreground">Floor Plan Extractor</h3>
                  <p className="text-sm text-muted-foreground mt-0.5">PDF & image floor plans</p>
                </div>
              </div>
              <p className="text-sm text-muted-foreground leading-relaxed mb-5">
                Smart OCR with spatial block grouping reads your floor plan and extracts every booth —
                number, exhibitor name (if listed), dimensions, and area m².
                Automatically filters out toilets, entrances, corridors, and all facilities.
                Works with dense multi-page PDFs and image scans.
              </p>
              <div className="flex flex-wrap gap-1.5 mb-6">
                {["PDF", "PNG", "JPG", "PSM-11 OCR", "Spatial Blocks", "Auto-Filter"].map((tag) => (
                  <span key={tag} className="tag-blue px-2.5 py-0.5 text-xs rounded-md font-medium">{tag}</span>
                ))}
              </div>
              <Link href="/dashboard/floorplan">
                <Button variant="outline" size="sm" className="border-primary/25 text-primary hover:bg-primary/6 font-medium">
                  Open Tool →
                </Button>
              </Link>
            </div>

            {/* Scraper Card */}
            <div className="card-elevated rounded-2xl p-8 group hover:shadow-lg hover:shadow-[oklch(0.52_0.160_185)/0.08] transition-all duration-300">
              <div className="flex items-start gap-4 mb-5">
                <div className="w-12 h-12 rounded-xl bg-[oklch(0.52_0.160_185/0.08)] border border-[oklch(0.52_0.160_185/0.15)] flex items-center justify-center flex-shrink-0 group-hover:scale-105 transition-transform">
                  <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" className="text-chart-2">
                    <circle cx="12" cy="12" r="10" />
                    <path d="M2 12h20" />
                    <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z" />
                  </svg>
                </div>
                <div>
                  <h3 className="text-lg font-bold text-foreground">Exhibitor Web Scraper</h3>
                  <p className="text-sm text-muted-foreground mt-0.5">Any exhibitor directory URL</p>
                </div>
              </div>
              <p className="text-sm text-muted-foreground leading-relaxed mb-5">
                Scrape exhibitor directories with auto-pagination and detail page traversal.
                Extracts company names, booth numbers, contacts, social links, and more.
                Supports JavaScript-rendered pages via Playwright.
              </p>
              <div className="flex flex-wrap gap-1.5 mb-6">
                {["Auto-Pagination", "Detail Pages", "Contacts", "LinkedIn", "JS Support"].map((tag) => (
                  <span key={tag} className="tag-teal px-2.5 py-0.5 text-xs rounded-md font-medium">{tag}</span>
                ))}
              </div>
              <Link href="/dashboard/scraper">
                <Button variant="outline" size="sm" className="border-chart-2/25 text-chart-2 hover:bg-chart-2/6 font-medium">
                  Open Tool →
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* ── What Gets Extracted ──────────────────────────────────────── */}
      <section className="py-20" style={{ background: "oklch(0.975 0.006 240)" }}>
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-14">
            <h2 className="text-3xl sm:text-4xl font-bold tracking-tight mb-3">Every Data Point. Automatically.</h2>
            <p className="text-muted-foreground max-w-xl mx-auto text-sm">
              Spatial block grouping means nearby text is treated as one booth —
              booth number, name, dimensions and area all linked correctly.
            </p>
          </div>
          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {[
              {
                icon: <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round"><rect x="3" y="3" width="18" height="18" rx="2" /><path d="M9 3v18" /></svg>,
                title: "Booth Numbers",
                desc: "Any format: 4240, A-12, ST-102, SAJ09, AR-E10, 6A31, 1-A and more.",
              },
              {
                icon: <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" /><circle cx="12" cy="7" r="4" /></svg>,
                title: "Exhibitor Names",
                desc: "Extracts company names. If no name shown, booth still appears as 'No name listed'.",
              },
              {
                icon: <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round"><path d="M21 3H3v7h18V3z" /><path d="M21 14H3v7h18v-7z" /><path d="M12 3v18" /></svg>,
                title: "Dimensions",
                desc: "Picks up 14X14 M, 8x14 M, 10x23 M, 9X23 M — all dimension formats.",
              },
              {
                icon: <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z" /></svg>,
                title: "Area (m²)",
                desc: "Reads 196 sq.m., 112 sq.m., 255 sq.m. and all area notations.",
              },
              {
                icon: <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" /></svg>,
                title: "Hall / Pavilion",
                desc: "Identifies which hall, pavilion, or section each booth belongs to.",
              },
              {
                icon: <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round"><path d="M18.36 6.64A9 9 0 1 1 5.64 6.64" /><path d="M12 2v10" /></svg>,
                title: "Smart Filtering",
                desc: "Ignores toilets, entrances, exits, corridors, registration desks, and all facility text.",
              },
            ].map((item) => (
              <div key={item.title} className="card-elevated rounded-xl p-5 hover:shadow-md transition-shadow">
                <div className="w-9 h-9 rounded-lg bg-primary/8 border border-primary/12 flex items-center justify-center text-primary mb-3">
                  {item.icon}
                </div>
                <h4 className="font-semibold text-sm text-foreground mb-1.5">{item.title}</h4>
                <p className="text-xs text-muted-foreground leading-relaxed">{item.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── How It Works ─────────────────────────────────────────────── */}
      <section className="py-20 bg-white">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-14">
            <h2 className="text-3xl sm:text-4xl font-bold tracking-tight mb-3">How It Works</h2>
            <p className="text-muted-foreground text-sm max-w-md mx-auto">Floor plan to clean database in seconds.</p>
          </div>
          <div className="grid md:grid-cols-3 gap-8 relative">
            {[
              { n: "1", title: "Upload", desc: "Drop in your floor plan — PDF, PNG, or JPG. Any format, any show." },
              { n: "2", title: "Extract", desc: "Spatial OCR groups nearby text into booths. Fields are matched — number, name, size, area." },
              { n: "3", title: "Export", desc: "Download clean CSV, Excel, or JSON. Ready for CRM, logistics, or your sales team." },
            ].map((item, i) => (
              <div key={item.n} className="relative text-center px-4">
                {i < 2 && (
                  <div className="hidden md:block absolute top-7 left-[calc(50%+40px)] right-0 h-px bg-gradient-to-r from-border to-transparent" />
                )}
                <div className="w-14 h-14 rounded-2xl bg-primary/8 border border-primary/15 flex items-center justify-center mx-auto mb-5 text-2xl font-bold text-primary">
                  {item.n}
                </div>
                <h3 className="text-base font-bold text-foreground mb-2">{item.title}</h3>
                <p className="text-sm text-muted-foreground leading-relaxed">{item.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── Who It's For ─────────────────────────────────────────────── */}
      <section className="py-20" style={{ background: "oklch(0.975 0.006 240)" }}>
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-14">
            <h2 className="text-3xl sm:text-4xl font-bold tracking-tight mb-3">Built for Exhibition Professionals</h2>
            <p className="text-muted-foreground text-sm max-w-md mx-auto">Save hours on every show.</p>
          </div>
          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {[
              { title: "Stand Builders", desc: "Get exact booth dimensions and layouts from any floor plan instantly." },
              { title: "Marketing Agencies", desc: "Build exhibitor contact lists from any directory in minutes." },
              { title: "Logistics Teams", desc: "Structured hall and booth data for planning shipments and deliveries." },
              { title: "Sales Teams", desc: "Identify new leads with exhibitor names, booth info, and contact data." },
            ].map((item) => (
              <div key={item.title} className="card-elevated rounded-xl p-5 hover:shadow-md transition-shadow">
                <h4 className="font-bold text-sm text-foreground mb-2">{item.title}</h4>
                <p className="text-xs text-muted-foreground leading-relaxed">{item.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── Export Formats ────────────────────────────────────────────── */}
      <section className="py-20 bg-white">
        <div className="mx-auto max-w-5xl px-4 sm:px-6 lg:px-8">
          <div className="card-tinted rounded-2xl p-10 lg:p-14 text-center">
            <h2 className="text-2xl sm:text-3xl font-bold tracking-tight mb-3">Export in Any Format</h2>
            <p className="text-muted-foreground max-w-md mx-auto mb-10 text-sm">One click. Your data exactly how you need it.</p>
            <div className="flex flex-wrap items-center justify-center gap-4">
              {[
                { fmt: "CSV",  desc: "Spreadsheet ready",  color: "text-emerald-600" },
                { fmt: "XLSX", desc: "Formatted Excel",    color: "text-primary" },
                { fmt: "JSON", desc: "API & dev ready",    color: "text-chart-2" },
              ].map((item) => (
                <div key={item.fmt} className="flex items-center gap-3 px-5 py-3.5 rounded-xl card-elevated">
                  <div className={`w-10 h-10 rounded-lg bg-white border border-border flex items-center justify-center font-bold text-xs ${item.color}`}>
                    {item.fmt}
                  </div>
                  <div className="text-left">
                    <div className="text-sm font-semibold text-foreground">{item.fmt}</div>
                    <div className="text-xs text-muted-foreground">{item.desc}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* ── CTA ───────────────────────────────────────────────────────── */}
      <section className="py-24 text-center" style={{ background: "oklch(0.975 0.006 240)" }}>
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <h2 className="text-3xl sm:text-4xl font-bold tracking-tight mb-4">
            Ready to Extract <span className="gradient-text">Exhibition Data?</span>
          </h2>
          <p className="text-muted-foreground max-w-md mx-auto mb-8 text-sm">
            No sign-up. No API key. Upload your first floor plan and get results instantly.
          </p>
          <Link href="/dashboard">
            <Button
              size="lg"
              className="bg-primary hover:bg-primary/90 text-primary-foreground shadow-md shadow-primary/20 px-10 font-semibold animate-pulse-ring"
            >
              Open the App →
            </Button>
          </Link>
        </div>
      </section>
    </div>
  );
}
