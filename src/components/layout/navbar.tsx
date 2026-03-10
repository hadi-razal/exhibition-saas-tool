"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Button } from "@/components/ui/button";
import { useState } from "react";

const navLinks = [
    { href: "/", label: "Home" },
    { href: "/pricing", label: "Pricing" },
    { href: "/about", label: "About" },
];

export function Navbar() {
    const pathname = usePathname();
    const [mobileOpen, setMobileOpen] = useState(false);
    const isDashboard = pathname.startsWith("/dashboard");

    return (
        <header className="fixed top-0 left-0 right-0 z-50 border-b border-border/50 bg-background/80 backdrop-blur-xl">
            <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
                {/* Logo */}
                <Link href="/" className="flex items-center gap-2.5 group">
                    <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-primary/10 border border-primary/20 group-hover:bg-primary/20 transition-colors">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-primary">
                            <rect x="3" y="3" width="18" height="18" rx="2" />
                            <path d="M3 9h18" />
                            <path d="M9 21V9" />
                        </svg>
                    </div>
                    <span className="text-lg font-bold tracking-tight">
                        <span className="gradient-text">ExhibitIQ</span>
                    </span>
                </Link>

                {/* Desktop Nav */}
                <nav className="hidden md:flex items-center gap-1">
                    {navLinks.map((link) => (
                        <Link
                            key={link.href}
                            href={link.href}
                            className={`px-4 py-2 text-sm font-medium rounded-lg transition-colors ${pathname === link.href
                                    ? "text-primary bg-primary/10"
                                    : "text-muted-foreground hover:text-foreground hover:bg-accent/50"
                                }`}
                        >
                            {link.label}
                        </Link>
                    ))}
                </nav>

                {/* CTA */}
                <div className="hidden md:flex items-center gap-3">
                    {isDashboard ? (
                        <Link href="/">
                            <Button variant="ghost" size="sm">
                                ← Back to Site
                            </Button>
                        </Link>
                    ) : (
                        <Link href="/dashboard">
                            <Button size="sm" className="bg-primary hover:bg-primary/90 text-primary-foreground shadow-lg shadow-primary/25">
                                Open App →
                            </Button>
                        </Link>
                    )}
                </div>

                {/* Mobile toggle */}
                <button
                    className="md:hidden p-2 rounded-lg hover:bg-accent/50 transition-colors"
                    onClick={() => setMobileOpen(!mobileOpen)}
                    aria-label="Toggle menu"
                >
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" className="text-foreground">
                        {mobileOpen ? (
                            <>
                                <path d="M18 6L6 18" />
                                <path d="M6 6l12 12" />
                            </>
                        ) : (
                            <>
                                <path d="M4 6h16" />
                                <path d="M4 12h16" />
                                <path d="M4 18h16" />
                            </>
                        )}
                    </svg>
                </button>
            </div>

            {/* Mobile Menu */}
            {mobileOpen && (
                <div className="md:hidden border-t border-border/50 bg-background/95 backdrop-blur-xl">
                    <nav className="flex flex-col p-4 gap-1">
                        {navLinks.map((link) => (
                            <Link
                                key={link.href}
                                href={link.href}
                                onClick={() => setMobileOpen(false)}
                                className={`px-4 py-2.5 text-sm font-medium rounded-lg transition-colors ${pathname === link.href
                                        ? "text-primary bg-primary/10"
                                        : "text-muted-foreground hover:text-foreground hover:bg-accent/50"
                                    }`}
                            >
                                {link.label}
                            </Link>
                        ))}
                        <div className="pt-2 mt-2 border-t border-border/50">
                            <Link href="/dashboard" onClick={() => setMobileOpen(false)}>
                                <Button size="sm" className="w-full bg-primary hover:bg-primary/90 text-primary-foreground">
                                    Open App →
                                </Button>
                            </Link>
                        </div>
                    </nav>
                </div>
            )}
        </header>
    );
}
