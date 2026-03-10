"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Switch } from "@/components/ui/switch";
import { Label } from "@/components/ui/label";
import Link from "next/link";

interface AnalysisResult {
    pagination_detected: boolean;
    estimated_pages: number;
    detail_pages_detected: boolean;
    exhibitor_count_page1: number;
    detected_fields: string[];
    page_title: string;
    is_dynamic: boolean;
}

interface ExhibitorRow {
    company_name?: string;
    booth_number?: string;
    hall?: string;
    country?: string;
    city?: string;
    category?: string;
    website?: string;
    email?: string;
    phone?: string;
    linkedin?: string;
    profile_url?: string;
    description?: string;
    [key: string]: string | undefined;
}

interface ProgressUpdate {
    message: string;
    current_page?: number;
    total_pages?: number;
    exhibitors_found?: number;
}

type ScraperStep = "input" | "analyzing" | "confirm" | "scraping" | "results";

export default function ScraperPage() {
    const [url, setUrl] = useState("");
    const [step, setStep] = useState<ScraperStep>("input");
    const [analysis, setAnalysis] = useState<AnalysisResult | null>(null);
    const [results, setResults] = useState<ExhibitorRow[]>([]);
    const [progress, setProgress] = useState<ProgressUpdate | null>(null);
    const [error, setError] = useState<string | null>(null);
    const [searchTerm, setSearchTerm] = useState("");

    // User config
    const [maxPages, setMaxPages] = useState(10);
    const [followDetailPages, setFollowDetailPages] = useState(true);
    const [extractContacts, setExtractContacts] = useState(true);

    const handleAnalyze = async () => {
        if (!url.trim()) return;
        setStep("analyzing");
        setError(null);
        setAnalysis(null);

        try {
            const response = await fetch("/api/scraper/analyze", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ url: url.trim() }),
            });

            if (!response.ok) {
                const errData = await response.json().catch(() => ({}));
                throw new Error(errData.error || `Analysis failed: ${response.statusText}`);
            }

            const data = await response.json();
            setAnalysis(data);
            setMaxPages(data.estimated_pages || 10);
            setFollowDetailPages(data.detail_pages_detected);
            setStep("confirm");
        } catch (err) {
            setError(err instanceof Error ? err.message : "Analysis failed");
            setStep("input");
        }
    };

    const handleScrape = async () => {
        if (!url.trim()) return;
        setStep("scraping");
        setError(null);
        setResults([]);
        setProgress(null);

        try {
            const response = await fetch("/api/scraper/scrape", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    url: url.trim(),
                    max_pages: maxPages,
                    follow_detail_pages: followDetailPages,
                    extract_contacts: extractContacts,
                }),
            });

            if (!response.ok) throw new Error(`Scraping failed: ${response.statusText}`);

            const reader = response.body?.getReader();
            const decoder = new TextDecoder();
            if (!reader) throw new Error("No response stream");

            let buffer = "";
            while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                buffer += decoder.decode(value, { stream: true });
                const lines = buffer.split("\n");
                buffer = lines.pop() || "";

                for (const line of lines) {
                    if (line.startsWith("data: ")) {
                        try {
                            const data = JSON.parse(line.slice(6));

                            if (data.type === "progress") {
                                setProgress(data);
                            } else if (data.type === "result") {
                                setResults(data.rows || []);
                                setStep("results");
                            } else if (data.type === "error") {
                                throw new Error(data.message);
                            }
                        } catch (parseError) {
                            if (parseError instanceof SyntaxError) continue;
                            throw parseError;
                        }
                    }
                }
            }

            if (step !== "results") setStep("results");
        } catch (err) {
            setError(err instanceof Error ? err.message : "Scraping failed");
            setStep("input");
        }
    };

    const handleExport = async (format: "csv" | "excel" | "json") => {
        if (results.length === 0) return;
        try {
            const response = await fetch("/api/scraper/export", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ rows: results, format }),
            });
            if (!response.ok) throw new Error("Export failed");
            const blob = await response.blob();
            const blobUrl = URL.createObjectURL(blob);
            const a = document.createElement("a");
            a.href = blobUrl;
            a.download = `exhibitor-scrape-results.${format === "excel" ? "xlsx" : format}`;
            a.click();
            URL.revokeObjectURL(blobUrl);
        } catch {
            setError("Export failed. Please try again.");
        }
    };

    const handleReset = () => {
        setStep("input");
        setUrl("");
        setAnalysis(null);
        setResults([]);
        setProgress(null);
        setError(null);
        setSearchTerm("");
    };

    const filteredResults = results.filter((row) =>
        Object.values(row).some((val) =>
            String(val || "").toLowerCase().includes(searchTerm.toLowerCase())
        )
    );

    const columns = results.length > 0 ? Object.keys(results[0]) : [];

    // Summary stats
    const totalExhibitors = results.length;
    const emailsFound = results.filter((r) => r.email).length;
    const websitesFound = results.filter((r) => r.website).length;
    const linkedinFound = results.filter((r) => r.linkedin).length;
    const countriesFound = new Set(results.map((r) => r.country).filter(Boolean)).size;

    return (
        <div className="py-12">
            <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
                {/* Header */}
                <div className="flex items-center gap-3 mb-8">
                    <Link href="/dashboard">
                        <Button variant="ghost" size="sm" className="text-muted-foreground hover:text-foreground">
                            ← Dashboard
                        </Button>
                    </Link>
                    <div>
                        <h1 className="text-2xl font-bold">Exhibitor Web Scraper</h1>
                        <p className="text-sm text-muted-foreground">Paste an exhibitor directory URL and extract structured data</p>
                    </div>
                </div>

                {/* Step 1: URL Input */}
                {(step === "input" || step === "analyzing") && (
                    <div className="max-w-2xl mx-auto">
                        <div className="glass-card rounded-2xl p-8">
                            <h2 className="text-lg font-semibold mb-2">Step 1: Enter URL</h2>
                            <p className="text-sm text-muted-foreground mb-6">
                                Paste an exhibitor directory or listing page URL. We&apos;ll analyze the page structure first.
                            </p>

                            <div className="space-y-4">
                                <input
                                    type="url"
                                    value={url}
                                    onChange={(e) => setUrl(e.target.value)}
                                    placeholder="https://example.com/exhibitors"
                                    className="w-full px-4 py-3 text-sm rounded-lg bg-input border border-border/50 focus:border-primary/50 focus:outline-none"
                                    disabled={step === "analyzing"}
                                />

                                <Button
                                    onClick={handleAnalyze}
                                    disabled={!url.trim() || step === "analyzing"}
                                    className="w-full bg-chart-2 hover:bg-chart-2/90 text-white shadow-lg"
                                >
                                    {step === "analyzing" ? (
                                        <span className="flex items-center gap-2">
                                            <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
                                                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                                                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                                            </svg>
                                            Analyzing Page...
                                        </span>
                                    ) : (
                                        "Analyze Page →"
                                    )}
                                </Button>
                            </div>

                            {error && (
                                <div className="mt-4 rounded-lg bg-destructive/10 border border-destructive/20 p-3">
                                    <p className="text-sm text-destructive">{error}</p>
                                </div>
                            )}
                        </div>
                    </div>
                )}

                {/* Step 2: Analysis & Confirm */}
                {step === "confirm" && analysis && (
                    <div className="max-w-2xl mx-auto">
                        <div className="glass-card rounded-2xl p-8">
                            <h2 className="text-lg font-semibold mb-2">Step 2: Review & Configure</h2>
                            <p className="text-sm text-muted-foreground mb-6">
                                We analyzed the page. Here&apos;s what we found:
                            </p>

                            {/* Analysis Summary */}
                            <div className="space-y-3 mb-8">
                                <div className="flex items-center justify-between p-3 rounded-lg bg-card border border-border/50">
                                    <span className="text-sm">Page Title</span>
                                    <span className="text-sm font-medium truncate ml-4 max-w-[200px]">{analysis.page_title || "—"}</span>
                                </div>
                                <div className="flex items-center justify-between p-3 rounded-lg bg-card border border-border/50">
                                    <span className="text-sm">Exhibitors Found (Page 1)</span>
                                    <span className="text-sm font-bold text-chart-2">{analysis.exhibitor_count_page1}</span>
                                </div>
                                <div className="flex items-center justify-between p-3 rounded-lg bg-card border border-border/50">
                                    <span className="text-sm">Pagination Detected</span>
                                    <span className={`text-sm font-medium ${analysis.pagination_detected ? "text-green-400" : "text-muted-foreground"}`}>
                                        {analysis.pagination_detected ? `Yes — ~${analysis.estimated_pages} pages` : "No"}
                                    </span>
                                </div>
                                <div className="flex items-center justify-between p-3 rounded-lg bg-card border border-border/50">
                                    <span className="text-sm">Detail Sub-Pages</span>
                                    <span className={`text-sm font-medium ${analysis.detail_pages_detected ? "text-green-400" : "text-muted-foreground"}`}>
                                        {analysis.detail_pages_detected ? "Yes — exhibitor cards link to profile pages" : "No"}
                                    </span>
                                </div>
                                <div className="flex items-center justify-between p-3 rounded-lg bg-card border border-border/50">
                                    <span className="text-sm">Page Type</span>
                                    <span className="text-sm font-medium">{analysis.is_dynamic ? "Dynamic (JS)" : "Static (HTML)"}</span>
                                </div>
                                {analysis.detected_fields.length > 0 && (
                                    <div className="p-3 rounded-lg bg-card border border-border/50">
                                        <span className="text-sm block mb-2">Detected Fields</span>
                                        <div className="flex flex-wrap gap-1.5">
                                            {analysis.detected_fields.map((field) => (
                                                <span key={field} className="px-2 py-0.5 text-xs rounded bg-chart-2/10 text-chart-2 border border-chart-2/15">
                                                    {field}
                                                </span>
                                            ))}
                                        </div>
                                    </div>
                                )}
                            </div>

                            {/* Configuration */}
                            <div className="space-y-4 mb-8 p-4 rounded-lg bg-muted/30 border border-border/30">
                                <h3 className="text-sm font-semibold">Scraping Options</h3>

                                {analysis.pagination_detected && (
                                    <div className="flex items-center justify-between">
                                        <Label htmlFor="maxPages" className="text-sm">Max pages to scrape</Label>
                                        <input
                                            id="maxPages"
                                            type="number"
                                            min={1}
                                            max={100}
                                            value={maxPages}
                                            onChange={(e) => setMaxPages(Number(e.target.value))}
                                            className="w-20 px-2 py-1 text-sm rounded bg-input border border-border/50 text-center"
                                        />
                                    </div>
                                )}

                                {analysis.detail_pages_detected && (
                                    <div className="flex items-center justify-between">
                                        <Label htmlFor="followDetail" className="text-sm">
                                            Follow detail pages
                                            <span className="block text-xs text-muted-foreground">Visit each exhibitor profile for more data</span>
                                        </Label>
                                        <Switch
                                            id="followDetail"
                                            checked={followDetailPages}
                                            onCheckedChange={setFollowDetailPages}
                                        />
                                    </div>
                                )}

                                <div className="flex items-center justify-between">
                                    <Label htmlFor="extractContacts" className="text-sm">
                                        Extract contacts & social
                                        <span className="block text-xs text-muted-foreground">Email, phone, LinkedIn, social links</span>
                                    </Label>
                                    <Switch
                                        id="extractContacts"
                                        checked={extractContacts}
                                        onCheckedChange={setExtractContacts}
                                    />
                                </div>
                            </div>

                            <div className="flex gap-3">
                                <Button
                                    variant="outline"
                                    onClick={() => setStep("input")}
                                    className="flex-1"
                                >
                                    ← Back
                                </Button>
                                <Button
                                    onClick={handleScrape}
                                    className="flex-1 bg-chart-2 hover:bg-chart-2/90 text-white shadow-lg"
                                >
                                    Start Full Scrape →
                                </Button>
                            </div>
                        </div>
                    </div>
                )}

                {/* Step 3: Scraping Progress */}
                {step === "scraping" && (
                    <div className="max-w-2xl mx-auto">
                        <div className="glass-card rounded-2xl p-8 text-center">
                            <svg className="animate-spin h-12 w-12 text-chart-2 mx-auto mb-6" viewBox="0 0 24 24">
                                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                            </svg>

                            <h2 className="text-lg font-semibold mb-2">Scraping in Progress</h2>

                            {progress && (
                                <div className="mt-4 space-y-2">
                                    <p className="text-sm text-muted-foreground">{progress.message}</p>
                                    {progress.current_page !== undefined && progress.total_pages !== undefined && (
                                        <div className="space-y-1">
                                            <div className="w-full h-2 bg-muted rounded-full overflow-hidden">
                                                <div
                                                    className="h-full bg-chart-2 rounded-full transition-all duration-300"
                                                    style={{ width: `${(progress.current_page / progress.total_pages) * 100}%` }}
                                                />
                                            </div>
                                            <p className="text-xs text-muted-foreground">
                                                Page {progress.current_page} of {progress.total_pages}
                                                {progress.exhibitors_found !== undefined && ` • ${progress.exhibitors_found} exhibitors found`}
                                            </p>
                                        </div>
                                    )}
                                </div>
                            )}

                            {error && (
                                <div className="mt-4 rounded-lg bg-destructive/10 border border-destructive/20 p-3">
                                    <p className="text-sm text-destructive">{error}</p>
                                </div>
                            )}
                        </div>
                    </div>
                )}

                {/* Step 4: Results */}
                {step === "results" && (
                    <div className="space-y-6">
                        {/* Summary Cards */}
                        <div className="grid grid-cols-2 sm:grid-cols-5 gap-3">
                            <div className="glass-card rounded-lg p-4">
                                <div className="text-2xl font-bold">{totalExhibitors}</div>
                                <div className="text-xs text-muted-foreground">Total Exhibitors</div>
                            </div>
                            <div className="glass-card rounded-lg p-4">
                                <div className="text-2xl font-bold">{emailsFound}</div>
                                <div className="text-xs text-muted-foreground">Emails Found</div>
                            </div>
                            <div className="glass-card rounded-lg p-4">
                                <div className="text-2xl font-bold">{websitesFound}</div>
                                <div className="text-xs text-muted-foreground">Websites Found</div>
                            </div>
                            <div className="glass-card rounded-lg p-4">
                                <div className="text-2xl font-bold">{linkedinFound}</div>
                                <div className="text-xs text-muted-foreground">LinkedIn Profiles</div>
                            </div>
                            <div className="glass-card rounded-lg p-4">
                                <div className="text-2xl font-bold">{countriesFound}</div>
                                <div className="text-xs text-muted-foreground">Countries</div>
                            </div>
                        </div>

                        {/* Search & Export & Reset */}
                        <div className="flex flex-col sm:flex-row gap-3 items-start sm:items-center justify-between">
                            <div className="flex gap-3 items-center">
                                <input
                                    type="text"
                                    placeholder="Search results..."
                                    value={searchTerm}
                                    onChange={(e) => setSearchTerm(e.target.value)}
                                    className="w-64 px-3 py-2 text-sm rounded-lg bg-input border border-border/50 focus:border-chart-2/50 focus:outline-none"
                                />
                                <Button variant="ghost" size="sm" onClick={handleReset} className="text-muted-foreground">
                                    New Scrape
                                </Button>
                            </div>
                            <div className="flex gap-2">
                                <Button variant="outline" size="sm" onClick={() => handleExport("csv")}>CSV</Button>
                                <Button variant="outline" size="sm" onClick={() => handleExport("excel")}>Excel</Button>
                                <Button variant="outline" size="sm" onClick={() => handleExport("json")}>JSON</Button>
                            </div>
                        </div>

                        {/* Results Table */}
                        <div className="glass-card rounded-xl overflow-hidden">
                            <div className="overflow-x-auto">
                                <table className="w-full text-sm">
                                    <thead>
                                        <tr className="border-b border-border/50 bg-card/50">
                                            {columns.map((col) => (
                                                <th key={col} className="text-left px-4 py-3 text-xs font-semibold text-muted-foreground uppercase tracking-wider whitespace-nowrap">
                                                    {col.replace(/_/g, " ")}
                                                </th>
                                            ))}
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {filteredResults.map((row, i) => (
                                            <tr key={i} className="border-b border-border/30 hover:bg-card/30 transition-colors">
                                                {columns.map((col) => (
                                                    <td key={col} className="px-4 py-3 whitespace-nowrap max-w-[200px] truncate">
                                                        {col === "website" || col === "linkedin" || col === "profile_url" ? (
                                                            row[col] ? (
                                                                <a href={row[col]} target="_blank" rel="noopener noreferrer" className="text-chart-2 hover:underline">
                                                                    {row[col]}
                                                                </a>
                                                            ) : "—"
                                                        ) : (
                                                            String(row[col] ?? "—")
                                                        )}
                                                    </td>
                                                ))}
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>
                        </div>

                        {filteredResults.length === 0 && results.length > 0 && (
                            <p className="text-center text-sm text-muted-foreground py-8">
                                No results match your search &quot;{searchTerm}&quot;
                            </p>
                        )}
                    </div>
                )}
            </div>
        </div>
    );
}
