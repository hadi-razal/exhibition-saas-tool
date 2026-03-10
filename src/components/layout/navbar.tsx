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
        <header className="fixed top-0 left-0 right-0 z-50 glass border-b border-border/50">
            <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
                {/* Logo */}
                <Link href="/" className="flex items-center gap-3 group">
                    <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-primary/10 border border-primary/20 group-hover:bg-primary/15 group-hover:scale-105 transition-all duration-300 shadow-inner">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" className="text-primary">
                            <rect x="3" y="3" width="18" height="18" rx="3" />
                            <path d="M3 9h18" />
                            <path d="M9 21V9" />
                        </svg>
                    </div>
                    <span className="text-xl font-extrabold tracking-tight gradient-text">ExhibitIQ</span>
                </Link>

                {/* Desktop Nav */}
                <nav className="hidden md:flex items-center gap-1">
                    {navLinks.map((link) => (
                        <Link
                            key={link.href}
                            href={link.href}
                            className={`px-4 py-2 text-sm font-semibold rounded-xl transition-all duration-300 ${pathname === link.href
                                    ? "text-primary bg-primary/10 shadow-sm"
                                    : "text-muted-foreground hover:text-foreground hover:bg-accent hover:shadow-sm"
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
                            <Button variant="ghost" className="text-muted-foreground hover:text-foreground font-semibold rounded-xl transition-all">
                                ← Back to Site
                            </Button>
                        </Link>
                    ) : (
                        <Link href="/dashboard">
                            <Button
                                className="bg-primary hover:bg-primary/90 text-primary-foreground shadow-md shadow-primary/20 font-bold rounded-xl px-6 transition-all hover:-translate-y-0.5"
                            >
                                Open App →
                            </Button>
                        </Link>
                    )}
                </div>

                {/* Mobile toggle */}
                <button
                    className="md:hidden p-2 rounded-xl hover:bg-accent transition-colors"
                    onClick={() => setMobileOpen(!mobileOpen)}
                    aria-label="Toggle menu"
                >
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" className="text-foreground">
                        {mobileOpen ? (
                            <><path d="M18 6L6 18" /><path d="M6 6l12 12" /></>
                        ) : (
                            <><path d="M4 6h16" /><path d="M4 12h16" /><path d="M4 18h16" /></>
                        )}
                    </svg>
                </button>
            </div>

            {/* Mobile Menu */}
            {mobileOpen && (
                <div className="md:hidden border-t border-border/50 glass">
                    <nav className="flex flex-col p-4 gap-2">
                        {navLinks.map((link) => (
                            <Link
                                key={link.href}
                                href={link.href}
                                onClick={() => setMobileOpen(false)}
                                className={`px-4 py-3 text-sm font-semibold rounded-xl transition-all ${pathname === link.href
                                        ? "text-primary bg-primary/10"
                                        : "text-muted-foreground hover:text-foreground hover:bg-accent"
                                    }`}
                            >
                                {link.label}
                            </Link>
                        ))}
                        <div className="pt-3 mt-2 border-t border-border/50">
                            <Link href="/dashboard" onClick={() => setMobileOpen(false)}>
                                <Button className="w-full bg-primary hover:bg-primary/90 text-primary-foreground rounded-xl font-bold h-12 shadow-sm">
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
