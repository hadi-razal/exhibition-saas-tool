import Link from "next/link";

export function Footer() {
    return (
        <footer className="border-t border-border/60 bg-white">
            <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-16">
                <div className="grid grid-cols-1 md:grid-cols-4 gap-12">
                    {/* Brand */}
                    <div className="md:col-span-1">
                        <Link href="/" className="flex items-center gap-3 mb-6 group">
                            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-primary/10 border border-primary/20 group-hover:scale-105 transition-transform">
                                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" className="text-primary">
                                    <rect x="3" y="3" width="18" height="18" rx="3" />
                                    <path d="M3 9h18" />
                                    <path d="M9 21V9" />
                                </svg>
                            </div>
                            <span className="text-xl font-extrabold gradient-text">ExhibitIQ</span>
                        </Link>
                        <p className="text-sm text-muted-foreground leading-relaxed font-light">
                            Intelligent extraction tools for the exhibition and trade show industry.
                        </p>
                    </div>

                    {/* Product */}
                    <div>
                        <h4 className="text-base font-bold mb-5 text-foreground">Product</h4>
                        <ul className="space-y-3">
                            <li><Link href="/dashboard/floorplan" className="text-sm text-muted-foreground hover:text-primary transition-colors font-medium">Floor Plan Extractor</Link></li>
                            <li><Link href="/dashboard/scraper" className="text-sm text-muted-foreground hover:text-primary transition-colors font-medium">Exhibitor Scraper</Link></li>
                            <li><Link href="/pricing" className="text-sm text-muted-foreground hover:text-primary transition-colors font-medium">Pricing</Link></li>
                        </ul>
                    </div>

                    {/* Company */}
                    <div>
                        <h4 className="text-base font-bold mb-5 text-foreground">Company</h4>
                        <ul className="space-y-3">
                            <li><Link href="/about" className="text-sm text-muted-foreground hover:text-primary transition-colors font-medium">About</Link></li>
                            <li><Link href="/" className="text-sm text-muted-foreground hover:text-primary transition-colors font-medium">Home</Link></li>
                        </ul>
                    </div>

                    {/* Legal */}
                    <div>
                        <h4 className="text-base font-bold mb-5 text-foreground">Legal</h4>
                        <ul className="space-y-3">
                            <li><span className="text-sm text-muted-foreground hover:text-primary transition-colors font-medium cursor-pointer">Privacy Policy</span></li>
                            <li><span className="text-sm text-muted-foreground hover:text-primary transition-colors font-medium cursor-pointer">Terms of Service</span></li>
                        </ul>
                    </div>
                </div>

                <div className="mt-16 pt-8 border-t border-border/60 flex flex-col sm:flex-row items-center justify-between gap-4">
                    <p className="text-sm text-muted-foreground font-light">
                        © {new Date().getFullYear()} ExhibitIQ. All rights reserved.
                    </p>
                    <p className="text-sm text-muted-foreground bg-primary/5 px-4 py-1.5 rounded-full border border-primary/10 font-medium text-primary">
                        Built for the exhibition industry.
                    </p>
                </div>
            </div>
        </footer>
    );
}
