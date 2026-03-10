import Link from "next/link";

export function Footer() {
    return (
        <footer className="border-t border-border/50 bg-background/50">
            <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-12">
                <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
                    {/* Brand */}
                    <div className="md:col-span-1">
                        <Link href="/" className="flex items-center gap-2.5 mb-4">
                            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary/10 border border-primary/20">
                                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-primary">
                                    <rect x="3" y="3" width="18" height="18" rx="2" />
                                    <path d="M3 9h18" />
                                    <path d="M9 21V9" />
                                </svg>
                            </div>
                            <span className="text-base font-bold gradient-text">ExhibitIQ</span>
                        </Link>
                        <p className="text-sm text-muted-foreground leading-relaxed">
                            Intelligent extraction tools for the exhibition and trade show industry.
                        </p>
                    </div>

                    {/* Product */}
                    <div>
                        <h4 className="text-sm font-semibold mb-4 text-foreground">Product</h4>
                        <ul className="space-y-2.5">
                            <li><Link href="/dashboard/floorplan" className="text-sm text-muted-foreground hover:text-foreground transition-colors">Floor Plan Extractor</Link></li>
                            <li><Link href="/dashboard/scraper" className="text-sm text-muted-foreground hover:text-foreground transition-colors">Exhibitor Scraper</Link></li>
                            <li><Link href="/pricing" className="text-sm text-muted-foreground hover:text-foreground transition-colors">Pricing</Link></li>
                        </ul>
                    </div>

                    {/* Company */}
                    <div>
                        <h4 className="text-sm font-semibold mb-4 text-foreground">Company</h4>
                        <ul className="space-y-2.5">
                            <li><Link href="/about" className="text-sm text-muted-foreground hover:text-foreground transition-colors">About</Link></li>
                            <li><Link href="/" className="text-sm text-muted-foreground hover:text-foreground transition-colors">Home</Link></li>
                        </ul>
                    </div>

                    {/* Legal */}
                    <div>
                        <h4 className="text-sm font-semibold mb-4 text-foreground">Legal</h4>
                        <ul className="space-y-2.5">
                            <li><span className="text-sm text-muted-foreground">Privacy Policy</span></li>
                            <li><span className="text-sm text-muted-foreground">Terms of Service</span></li>
                        </ul>
                    </div>
                </div>

                <div className="mt-10 pt-8 border-t border-border/50 flex flex-col sm:flex-row items-center justify-between gap-4">
                    <p className="text-xs text-muted-foreground">
                        © {new Date().getFullYear()} ExhibitIQ. All rights reserved.
                    </p>
                    <p className="text-xs text-muted-foreground">
                        Built for the exhibition industry.
                    </p>
                </div>
            </div>
        </footer>
    );
}
