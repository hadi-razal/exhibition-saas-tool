import type { Metadata } from "next";

export const metadata: Metadata = {
    title: "About — ExhibitIQ",
    description: "Learn about ExhibitIQ, the exhibition intelligence platform built for trade show professionals.",
};

export default function AboutPage() {
    return (
        <div className="py-24">
            <div className="mx-auto max-w-4xl px-4 sm:px-6 lg:px-8">
                {/* Header */}
                <div className="text-center mb-16">
                    <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full border border-primary/20 bg-primary/5 text-sm text-primary mb-6">
                        About
                    </div>
                    <h1 className="text-4xl sm:text-5xl font-bold mb-6">
                        Exhibition Intelligence,{" "}
                        <span className="gradient-text">Simplified</span>
                    </h1>
                    <p className="text-lg text-muted-foreground max-w-2xl mx-auto leading-relaxed">
                        ExhibitIQ helps exhibition professionals turn raw floor plans and exhibitor directories into
                        actionable, structured data — in minutes instead of hours.
                    </p>
                </div>

                {/* Content */}
                <div className="space-y-12">
                    {/* What We Do */}
                    <section className="glass-card rounded-2xl p-8">
                        <h2 className="text-2xl font-bold mb-4">What ExhibitIQ Does</h2>
                        <p className="text-muted-foreground leading-relaxed mb-4">
                            The exhibition and trade show industry generates massive amounts of unstructured data —
                            floor plans locked in PDFs, exhibitor listings scattered across websites, booth data buried in scanned images.
                        </p>
                        <p className="text-muted-foreground leading-relaxed">
                            ExhibitIQ provides two powerful tools to extract this data automatically:
                        </p>
                        <div className="grid sm:grid-cols-2 gap-6 mt-6">
                            <div className="p-5 rounded-xl bg-card border border-border/50">
                                <h3 className="font-semibold mb-2 text-primary">Floor Plan OCR Extractor</h3>
                                <p className="text-sm text-muted-foreground leading-relaxed">
                                    Upload any floor plan (PDF, PNG, JPG) and our multi-layered extraction engine
                                    uses direct text parsing, OCR, and intelligent pattern matching to pull out
                                    booth numbers, sizes, exhibitor names, hall info, and more.
                                </p>
                            </div>
                            <div className="p-5 rounded-xl bg-card border border-border/50">
                                <h3 className="font-semibold mb-2 text-chart-2">Exhibitor Web Scraper</h3>
                                <p className="text-sm text-muted-foreground leading-relaxed">
                                    Paste an exhibitor directory URL and the scraper auto-detects page structure,
                                    handles pagination, follows detail pages, and extracts company names, contacts,
                                    social links, booth numbers, and all available exhibitor data.
                                </p>
                            </div>
                        </div>
                    </section>

                    {/* Who It's For */}
                    <section className="glass-card rounded-2xl p-8">
                        <h2 className="text-2xl font-bold mb-4">Who It&apos;s For</h2>
                        <div className="grid sm:grid-cols-2 gap-4">
                            {[
                                { title: "Exhibition Stand Builders", desc: "Quickly extract booth dimensions, locations, and layouts from floor plans." },
                                { title: "Exhibition Agencies", desc: "Build comprehensive exhibitor databases from any directory or listing page." },
                                { title: "Marketing Teams", desc: "Get exhibitor contact info, LinkedIn profiles, and company details for outreach." },
                                { title: "Logistics Companies", desc: "Understand hall layouts, booth sizes, and placement data for planning." },
                                { title: "Exhibition Sales Teams", desc: "Identify leads with full company profiles, booth numbers, and contact data." },
                                { title: "Event Organizers", desc: "Digitize and structure floor plan data for internal systems." },
                            ].map((item) => (
                                <div key={item.title} className="p-4 rounded-lg bg-card/50 border border-border/30">
                                    <h4 className="font-semibold text-sm mb-1">{item.title}</h4>
                                    <p className="text-xs text-muted-foreground">{item.desc}</p>
                                </div>
                            ))}
                        </div>
                    </section>

                    {/* How Floor Plan Extraction Works */}
                    <section className="glass-card rounded-2xl p-8">
                        <h2 className="text-2xl font-bold mb-4">How Floor Plan Extraction Works</h2>
                        <div className="space-y-4">
                            {[
                                { step: "1", title: "Upload", desc: "Upload a floor plan as PDF, PNG, JPG, or JPEG." },
                                { step: "2", title: "Detect", desc: "System detects if the file is text-based or image-based." },
                                { step: "3", title: "Extract Text", desc: "For text-based PDFs, direct text extraction is used. For images/scans, OCR is applied." },
                                { step: "4", title: "Pattern Match", desc: "Regex and heuristics identify booth numbers (A12, B-14, H5-B13), sizes (3x3, 12 sqm), halls, and exhibitor names." },
                                { step: "5", title: "Structure", desc: "Results are organized into clean rows with booth number, size, exhibitor, hall, zone, and more." },
                                { step: "6", title: "Export", desc: "Download as CSV, Excel, or JSON for immediate use." },
                            ].map((item) => (
                                <div key={item.step} className="flex items-start gap-4">
                                    <div className="w-8 h-8 rounded-full bg-primary/10 border border-primary/20 flex items-center justify-center text-primary text-sm font-bold flex-shrink-0">
                                        {item.step}
                                    </div>
                                    <div>
                                        <h4 className="font-semibold text-sm">{item.title}</h4>
                                        <p className="text-sm text-muted-foreground">{item.desc}</p>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </section>

                    {/* How Web Scraping Works */}
                    <section className="glass-card rounded-2xl p-8">
                        <h2 className="text-2xl font-bold mb-4">How Exhibitor Scraping Works</h2>
                        <div className="space-y-4">
                            {[
                                { step: "1", title: "Paste URL", desc: "Enter any exhibitor directory or listing page URL." },
                                { step: "2", title: "Analyze", desc: "The system loads the page and auto-detects pagination, listing structure, and detail page links." },
                                { step: "3", title: "Confirm", desc: "You review what was detected and can adjust settings — max pages, follow detail pages, extract contacts." },
                                { step: "4", title: "Scrape", desc: "The engine scrapes all listing pages, follows detail links, and extracts all available fields." },
                                { step: "5", title: "Normalize", desc: "Data is cleaned, deduplicated, and structured into a consistent format." },
                                { step: "6", title: "Export", desc: "Download the complete exhibitor database as CSV, Excel, or JSON." },
                            ].map((item) => (
                                <div key={item.step} className="flex items-start gap-4">
                                    <div className="w-8 h-8 rounded-full bg-chart-2/10 border border-chart-2/20 flex items-center justify-center text-chart-2 text-sm font-bold flex-shrink-0">
                                        {item.step}
                                    </div>
                                    <div>
                                        <h4 className="font-semibold text-sm">{item.title}</h4>
                                        <p className="text-sm text-muted-foreground">{item.desc}</p>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </section>

                    {/* Limitations & Future */}
                    <section className="glass-card rounded-2xl p-8">
                        <h2 className="text-2xl font-bold mb-4">Current Limitations & Future Direction</h2>
                        <div className="grid sm:grid-cols-2 gap-6">
                            <div>
                                <h3 className="font-semibold text-sm mb-3 text-destructive">Known Limitations</h3>
                                <ul className="space-y-2">
                                    {[
                                        "OCR accuracy depends on image quality and resolution",
                                        "Complex/overlapping floor plans may need manual review",
                                        "Some heavily JS-protected sites may block scraping",
                                        "Scraping results depend on page structure consistency",
                                    ].map((item) => (
                                        <li key={item} className="flex items-start gap-2 text-sm text-muted-foreground">
                                            <span className="text-destructive mt-1">•</span>
                                            {item}
                                        </li>
                                    ))}
                                </ul>
                            </div>
                            <div>
                                <h3 className="font-semibold text-sm mb-3 text-primary">Future Plans</h3>
                                <ul className="space-y-2">
                                    {[
                                        "AI-powered booth boundary detection",
                                        "Multi-language OCR support",
                                        "Scheduled / automated scraping jobs",
                                        "CRM integrations for direct lead import",
                                        "Team collaboration features",
                                        "Cloud-hosted processing for faster jobs",
                                    ].map((item) => (
                                        <li key={item} className="flex items-start gap-2 text-sm text-muted-foreground">
                                            <span className="text-primary mt-1">•</span>
                                            {item}
                                        </li>
                                    ))}
                                </ul>
                            </div>
                        </div>
                    </section>
                </div>
            </div>
        </div>
    );
}
