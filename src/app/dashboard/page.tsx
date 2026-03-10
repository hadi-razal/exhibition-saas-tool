import Link from "next/link";
import { Button } from "@/components/ui/button";
import type { Metadata } from "next";

export const metadata: Metadata = {
    title: "Dashboard — ExhibitIQ",
    description: "Access your exhibition intelligence tools — Floor Plan Extractor and Exhibitor Web Scraper.",
};

export default function DashboardPage() {
    return (
        <div className="py-12">
            <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
                {/* Header */}
                <div className="mb-10">
                    <h1 className="text-3xl font-bold mb-2">Dashboard</h1>
                    <p className="text-muted-foreground">
                        Choose a tool to start extracting exhibition intelligence.
                    </p>
                </div>

                {/* Tool Cards */}
                <div className="grid md:grid-cols-2 gap-6 lg:gap-8 mb-12">
                    {/* Floor Plan Tool */}
                    <Link href="/dashboard/floorplan" className="group">
                        <div className="glass-card rounded-2xl p-8 h-full hover:border-primary/30 transition-all duration-300 cursor-pointer">
                            <div className="flex items-start justify-between mb-6">
                                <div className="w-16 h-16 rounded-xl bg-primary/10 border border-primary/20 flex items-center justify-center group-hover:scale-110 transition-transform">
                                    <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" className="text-primary">
                                        <rect x="2" y="2" width="20" height="20" rx="2" />
                                        <path d="M2 8h20" />
                                        <path d="M8 2v20" />
                                        <path d="M14 8v6" />
                                        <path d="M8 14h6" />
                                    </svg>
                                </div>
                                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" className="text-muted-foreground group-hover:text-primary group-hover:translate-x-1 transition-all">
                                    <path d="M5 12h14" />
                                    <path d="M12 5l7 7-7 7" />
                                </svg>
                            </div>

                            <h2 className="text-xl font-semibold mb-2">Floor Plan OCR Extractor</h2>
                            <p className="text-muted-foreground text-sm leading-relaxed mb-6">
                                Upload exhibition floor plans (PDF, PNG, JPG) and extract booth numbers, sizes,
                                exhibitor names, hall information, and more using multi-layered OCR and pattern matching.
                            </p>

                            <div className="flex flex-wrap gap-2">
                                {["Upload PDF/Image", "OCR Processing", "Pattern Detection", "CSV/Excel/JSON Export"].map((tag) => (
                                    <span key={tag} className="px-2.5 py-1 text-xs rounded-md bg-primary/10 text-primary border border-primary/15">
                                        {tag}
                                    </span>
                                ))}
                            </div>
                        </div>
                    </Link>

                    {/* Scraper Tool */}
                    <Link href="/dashboard/scraper" className="group">
                        <div className="glass-card rounded-2xl p-8 h-full hover:border-chart-2/30 transition-all duration-300 cursor-pointer">
                            <div className="flex items-start justify-between mb-6">
                                <div className="w-16 h-16 rounded-xl bg-chart-2/10 border border-chart-2/20 flex items-center justify-center group-hover:scale-110 transition-transform">
                                    <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" className="text-chart-2">
                                        <circle cx="12" cy="12" r="10" />
                                        <path d="M2 12h20" />
                                        <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z" />
                                    </svg>
                                </div>
                                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" className="text-muted-foreground group-hover:text-chart-2 group-hover:translate-x-1 transition-all">
                                    <path d="M5 12h14" />
                                    <path d="M12 5l7 7-7 7" />
                                </svg>
                            </div>

                            <h2 className="text-xl font-semibold mb-2">Exhibitor Web Scraper</h2>
                            <p className="text-muted-foreground text-sm leading-relaxed mb-6">
                                Paste any exhibitor directory URL and extract company names, booth numbers, contacts,
                                LinkedIn profiles, and more — with auto-pagination and detail page traversal.
                            </p>

                            <div className="flex flex-wrap gap-2">
                                {["Auto-Detect Pages", "Detail Page Scraping", "Contact Extraction", "CSV/Excel/JSON Export"].map((tag) => (
                                    <span key={tag} className="px-2.5 py-1 text-xs rounded-md bg-chart-2/10 text-chart-2 border border-chart-2/15">
                                        {tag}
                                    </span>
                                ))}
                            </div>
                        </div>
                    </Link>
                </div>

                {/* Quick Stats */}
                <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                    {[
                        { label: "Floor Plans Processed", value: "—", icon: "📄" },
                        { label: "Booths Extracted", value: "—", icon: "🏢" },
                        { label: "Exhibitors Scraped", value: "—", icon: "🌐" },
                        { label: "Exports Downloaded", value: "—", icon: "📥" },
                    ].map((stat) => (
                        <div key={stat.label} className="glass-card rounded-xl p-5">
                            <div className="text-2xl mb-2">{stat.icon}</div>
                            <div className="text-2xl font-bold mb-1">{stat.value}</div>
                            <div className="text-xs text-muted-foreground">{stat.label}</div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
}
