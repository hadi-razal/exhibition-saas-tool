import Link from "next/link";
import { Button } from "@/components/ui/button";

export default function HomePage() {
  return (
    <div className="relative bg-background">
      {/* ── Hero ─────────────────────────────────────────────────────── */}
      <section className="relative overflow-hidden hero-bg dot-grid min-h-[90vh] flex flex-col justify-center">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 pt-20 pb-24 relative z-10">
          <div className="text-center max-w-4xl mx-auto">
            {/* Badge */}
            <div
              className="inline-flex items-center gap-2 px-4 py-2 rounded-full border border-primary/20 bg-primary/5 text-xs font-semibold text-primary mb-8 animate-fade-in-up shadow-sm backdrop-blur-sm"
            >
              <span className="relative flex h-2 w-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-primary opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2 w-2 bg-primary"></span>
              </span>
              Exhibition Intelligence Platform
            </div>

            <h1
              className="text-5xl sm:text-6xl lg:text-7xl font-extrabold tracking-tight leading-[1.05] mb-8 animate-fade-in-up text-foreground drop-shadow-sm"
              style={{ animationDelay: "0.1s" }}
            >
              Turn Floor Plans Into <br className="hidden sm:block" />
              <span className="gradient-text">Structured Data</span>
            </h1>

            <p
              className="text-lg sm:text-xl text-muted-foreground max-w-2xl mx-auto mb-12 leading-relaxed animate-fade-in-up font-light"
              style={{ animationDelay: "0.2s" }}
            >
              Upload any exhibition floor plan and extract every booth number,
              exhibitor name, dimensions, and area automatically.
              No API key. No cloud. Just Python.
            </p>

            <div
              className="flex flex-col sm:flex-row items-center justify-center gap-4 animate-fade-in-up"
              style={{ animationDelay: "0.3s" }}
            >
              <Link href="/dashboard">
                <Button
                  size="lg"
                  className="bg-primary hover:bg-primary/90 text-primary-foreground shadow-lg shadow-primary/30 px-10 h-14 text-base font-semibold transition-all hover:-translate-y-1 animate-pulse-ring rounded-xl"
                >
                  Start Extracting →
                </Button>
              </Link>
              <Link href="/about">
                <Button variant="outline" size="lg" className="px-10 h-14 text-base bg-white/50 backdrop-blur-md border border-border hover:bg-white/80 font-medium transition-all hover:-translate-y-1 rounded-xl shadow-sm">
                  Learn More
                </Button>
              </Link>
            </div>
          </div>

          {/* Feature pill strip */}
          <div
            className="flex flex-wrap items-center justify-center gap-3 mt-16 animate-fade-in-up"
            style={{ animationDelay: "0.4s" }}
          >
            {[
              "Booth Numbers", "Exhibitor Names", "Dimensions (m)",
              "Area (m²)", "Hall Info", "Filters Facilities",
              "Booth-Only Rows", "CSV · Excel · JSON",
            ].map((feat) => (
              <span key={feat} className="tag-neutral text-xs px-4 py-1.5 rounded-full font-medium shadow-sm bg-white/80 backdrop-blur-sm border-border/50">
                {feat}
              </span>
            ))}
          </div>
        </div>

        {/* Decorative Background Elements */}
        <div className="absolute top-1/4 left-10 w-72 h-72 bg-primary/20 rounded-full blur-3xl opacity-50 mix-blend-multiply animate-pulse"></div>
        <div className="absolute bottom-1/4 right-10 w-96 h-96 bg-cyan-400/20 rounded-full blur-3xl opacity-50 mix-blend-multiply animate-pulse" style={{ animationDelay: "1s" }}></div>
      </section>

      {/* ── Divider ──────────────────────────────────────────────────── */}
      <div className="divider mx-auto max-w-5xl opacity-50" />

      {/* ── Tools Section ────────────────────────────────────────────── */}
      <section className="py-28 surface-muted relative overflow-hidden">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 relative z-10">
          <div className="text-center mb-16">
            <h2 className="text-4xl sm:text-5xl font-extrabold tracking-tight mb-4 text-foreground drop-shadow-sm">Two Powerful Tools</h2>
            <p className="text-lg text-muted-foreground max-w-xl mx-auto font-light">
              Extract exhibition data from any source — floor plans or exhibitor directories.
            </p>
          </div>

          <div className="grid lg:grid-cols-2 gap-8">
            {/* Floor Plan Card */}
            <div className="card-elevated rounded-[2rem] p-10 group relative overflow-hidden bg-white">
              <div className="absolute top-0 right-0 w-64 h-64 bg-primary/5 rounded-bl-full -z-10 transition-transform group-hover:scale-110"></div>

              <div className="flex items-start gap-5 mb-6">
                <div className="w-14 h-14 rounded-2xl bg-primary/10 border border-primary/20 flex items-center justify-center flex-shrink-0 group-hover:scale-110 group-hover:rotate-3 transition-transform shadow-inner text-primary">
                  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <rect x="2" y="2" width="20" height="20" rx="4" />
                    <path d="M2 8h20" />
                    <path d="M8 2v20" />
                  </svg>
                </div>
                <div className="pt-2">
                  <h3 className="text-2xl font-bold text-foreground">Floor Plan Extractor</h3>
                  <p className="text-sm text-primary font-medium mt-1">PDF & image floor plans</p>
                </div>
              </div>
              <p className="text-base text-muted-foreground leading-relaxed mb-8 font-light">
                Smart OCR with spatial block grouping reads your floor plan and extracts every booth —
                number, exhibitor name (if listed), dimensions, and area m².
                Automatically filters out toilets, entrances, corridors, and all facilities.
                Works with dense multi-page PDFs and image scans.
              </p>
              <div className="flex flex-wrap gap-2 mb-8">
                {["PDF", "PNG", "JPG", "PSM-11 OCR", "Spatial Blocks", "Auto-Filter"].map((tag) => (
                  <span key={tag} className="tag-blue px-3 py-1 text-xs rounded-lg font-semibold shadow-sm">{tag}</span>
                ))}
              </div>
              <Link href="/dashboard/floorplan">
                <Button variant="outline" className="w-full sm:w-auto border-primary/20 text-primary hover:bg-primary hover:text-white font-semibold rounded-xl h-12 px-8 transition-colors shadow-sm">
                  Open Tool →
                </Button>
              </Link>
            </div>

            {/* Scraper Card */}
            <div className="card-elevated rounded-[2rem] p-10 group relative overflow-hidden bg-white">
              <div className="absolute top-0 right-0 w-64 h-64 bg-cyan-500/5 rounded-bl-full -z-10 transition-transform group-hover:scale-110"></div>

              <div className="flex items-start gap-5 mb-6">
                <div className="w-14 h-14 rounded-2xl bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center flex-shrink-0 group-hover:scale-110 group-hover:-rotate-3 transition-transform shadow-inner text-cyan-600">
                  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <circle cx="12" cy="12" r="10" />
                    <path d="M2 12h20" />
                    <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z" />
                  </svg>
                </div>
                <div className="pt-2">
                  <h3 className="text-2xl font-bold text-foreground">Exhibitor Web Scraper</h3>
                  <p className="text-sm text-cyan-600 font-medium mt-1">Any exhibitor directory URL</p>
                </div>
              </div>
              <p className="text-base text-muted-foreground leading-relaxed mb-8 font-light">
                Scrape exhibitor directories with auto-pagination and detail page traversal.
                Extracts company names, booth numbers, contacts, social links, and more.
                Supports JavaScript-rendered pages via Playwright.
              </p>
              <div className="flex flex-wrap gap-2 mb-8">
                {["Auto-Pagination", "Detail Pages", "Contacts", "LinkedIn", "JS Support"].map((tag) => (
                  <span key={tag} className="tag-teal px-3 py-1 text-xs rounded-lg font-semibold shadow-sm">{tag}</span>
                ))}
              </div>
              <Link href="/dashboard/scraper">
                <Button variant="outline" className="w-full sm:w-auto border-cyan-500/20 text-cyan-700 hover:bg-cyan-600 hover:text-white font-semibold rounded-xl h-12 px-8 transition-colors shadow-sm">
                  Open Tool →
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* ── What Gets Extracted ──────────────────────────────────────── */}
      <section className="py-28 relative bg-white">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 relative z-10">
          <div className="text-center mb-16">
            <h2 className="text-4xl sm:text-5xl font-extrabold tracking-tight mb-4 text-foreground">Every Data Point. <span className="gradient-text-alt">Automatically.</span></h2>
            <p className="text-lg text-muted-foreground max-w-2xl mx-auto font-light">
              Spatial block grouping means nearby text is treated as one booth —
              booth number, name, dimensions and area all linked correctly.
            </p>
          </div>
          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {[
              {
                icon: <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round"><rect x="3" y="3" width="18" height="18" rx="2" /><path d="M9 3v18" /></svg>,
                title: "Booth Numbers",
                desc: "Any format: 4240, A-12, ST-102, SAJ09, AR-E10, 6A31, 1-A and more.",
              },
              {
                icon: <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" /><circle cx="12" cy="7" r="4" /></svg>,
                title: "Exhibitor Names",
                desc: "Extracts company names. If no name shown, booth still appears as 'No name listed'.",
              },
              {
                icon: <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round"><path d="M21 3H3v7h18V3z" /><path d="M21 14H3v7h18v-7z" /><path d="M12 3v18" /></svg>,
                title: "Dimensions",
                desc: "Picks up 14X14 M, 8x14 M, 10x23 M, 9X23 M — all dimension formats.",
              },
              {
                icon: <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z" /></svg>,
                title: "Area (m²)",
                desc: "Reads 196 sq.m., 112 sq.m., 255 sq.m. and all area notations.",
              },
              {
                icon: <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" /></svg>,
                title: "Hall / Pavilion",
                desc: "Identifies which hall, pavilion, or section each booth belongs to.",
              },
              {
                icon: <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round"><path d="M18.36 6.64A9 9 0 1 1 5.64 6.64" /><path d="M12 2v10" /></svg>,
                title: "Smart Filtering",
                desc: "Ignores toilets, entrances, exits, corridors, registration desks, and all facility text.",
              },
            ].map((item) => (
              <div key={item.title} className="card-elevated rounded-2xl p-6 group">
                <div className="w-12 h-12 rounded-xl bg-primary/10 border border-primary/20 flex items-center justify-center text-primary mb-5 group-hover:scale-110 transition-transform shadow-inner">
                  {item.icon}
                </div>
                <h4 className="font-bold text-lg text-foreground mb-2">{item.title}</h4>
                <p className="text-sm text-muted-foreground leading-relaxed font-light">{item.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── How It Works ─────────────────────────────────────────────── */}
      <section className="py-28 surface-muted relative">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-20">
            <h2 className="text-4xl sm:text-5xl font-extrabold tracking-tight mb-4">How It <span className="text-primary">Works</span></h2>
            <p className="text-lg text-muted-foreground max-w-md mx-auto font-light">Floor plan to clean database in seconds.</p>
          </div>
          <div className="grid md:grid-cols-3 gap-10 relative">
            {[
              { n: "1", title: "Upload", desc: "Drop in your floor plan — PDF, PNG, or JPG. Any format, any show." },
              { n: "2", title: "Extract", desc: "Spatial OCR groups nearby text into booths. Fields are matched — number, name, size, area." },
              { n: "3", title: "Export", desc: "Download clean CSV, Excel, or JSON. Ready for CRM, logistics, or your sales team." },
            ].map((item, i) => (
              <div key={item.n} className="relative text-center px-4 group">
                {i < 2 && (
                  <div className="hidden md:block absolute top-10 left-[calc(50%+40px)] right-0 h-0.5 bg-gradient-to-r from-primary/30 to-transparent dashed-border" />
                )}
                <div className="w-20 h-20 rounded-3xl bg-white border border-border flex items-center justify-center mx-auto mb-6 text-3xl font-extrabold text-primary shadow-lg group-hover:-translate-y-2 transition-transform">
                  {item.n}
                </div>
                <h3 className="text-xl font-bold text-foreground mb-3">{item.title}</h3>
                <p className="text-base text-muted-foreground leading-relaxed font-light">{item.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── Export Formats ────────────────────────────────────────────── */}
      <section className="py-28 bg-white">
        <div className="mx-auto max-w-5xl px-4 sm:px-6 lg:px-8">
          <div className="card-elevated rounded-[2.5rem] p-12 lg:p-16 text-center relative overflow-hidden bg-white">
            <div className="absolute inset-0 bg-gradient-to-br from-primary/5 to-transparent"></div>
            <div className="relative z-10">
              <h2 className="text-3xl sm:text-4xl font-extrabold tracking-tight mb-4">Export in Any Format</h2>
              <p className="text-lg text-muted-foreground max-w-md mx-auto mb-12 font-light">One click. Your data exactly how you need it.</p>
              <div className="flex flex-wrap items-center justify-center gap-6">
                {[
                  { fmt: "CSV", desc: "Spreadsheet ready", color: "text-emerald-600", bg: "bg-emerald-50", border: "border-emerald-200" },
                  { fmt: "XLSX", desc: "Formatted Excel", color: "text-primary", bg: "bg-primary/5", border: "border-primary/20" },
                  { fmt: "JSON", desc: "API & dev ready", color: "text-cyan-600", bg: "bg-cyan-50", border: "border-cyan-200" },
                ].map((item) => (
                  <div key={item.fmt} className="flex items-center gap-4 px-6 py-4 rounded-2xl bg-white border border-border shadow-sm hover:shadow-md transition-shadow">
                    <div className={`w-12 h-12 rounded-xl ${item.bg} ${item.border} border flex items-center justify-center font-bold text-sm ${item.color}`}>
                      {item.fmt}
                    </div>
                    <div className="text-left">
                      <div className="text-base font-bold text-foreground">{item.fmt}</div>
                      <div className="text-sm font-medium text-muted-foreground">{item.desc}</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ── CTA ───────────────────────────────────────────────────────── */}
      <section className="py-32 text-center hero-bg border-t border-border">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 relative z-10">
          <h2 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold tracking-tight mb-6">
            Ready to Extract <br className="hidden sm:block" />
            <span className="gradient-text">Exhibition Data?</span>
          </h2>
          <p className="text-lg text-muted-foreground max-w-xl mx-auto mb-10 font-light">
            No sign-up. No API key. Upload your first floor plan and get results instantly.
          </p>
          <Link href="/dashboard">
            <Button
              size="lg"
              className="bg-primary hover:bg-primary/90 text-primary-foreground shadow-xl shadow-primary/30 px-12 h-16 text-lg font-bold animate-pulse-ring rounded-2xl transition-transform hover:-translate-y-1"
            >
              Open the App →
            </Button>
          </Link>
        </div>
      </section>
    </div>
  );
}
