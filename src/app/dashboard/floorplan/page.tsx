"use client";

import { useState, useCallback, useRef } from "react";
import { Button } from "@/components/ui/button";
import Link from "next/link";

interface ExtractedRow {
    page?: number;
    booth_number?: string;
    exhibitor_name?: string;
    booth_size?: string;
    area_sqm?: string;
    hall?: string;
    zone?: string;
    source?: string;
    [key: string]: string | number | undefined;
}

interface ProgressStep {
    label: string;
    status: "pending" | "active" | "done" | "error";
}

const PREFERRED_COLUMNS = ["booth_number", "exhibitor_name", "booth_size", "area_sqm", "hall", "zone", "page", "source"];

const COLUMN_LABELS: Record<string, string> = {
    booth_number:   "Booth No.",
    exhibitor_name: "Exhibitor Name",
    booth_size:     "Dimensions",
    area_sqm:       "Area (m²)",
    hall:           "Hall / Pavilion",
    zone:           "Zone",
    page:           "Page",
    source:         "Source",
};

export default function FloorPlanPage() {
    const [file, setFile] = useState<File | null>(null);
    const [preview, setPreview] = useState<string | null>(null);
    const [results, setResults] = useState<ExtractedRow[]>([]);
    const [progress, setProgress] = useState<ProgressStep[]>([]);
    const [isProcessing, setIsProcessing] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [searchTerm, setSearchTerm] = useState("");
    const fileInputRef = useRef<HTMLInputElement>(null);

    const handleFileSelect = useCallback((selectedFile: File) => {
        setFile(selectedFile);
        setResults([]);
        setError(null);
        setProgress([]);
        if (selectedFile.type.startsWith("image/")) {
            const reader = new FileReader();
            reader.onload = (e) => setPreview(e.target?.result as string);
            reader.readAsDataURL(selectedFile);
        } else {
            setPreview(null);
        }
    }, []);

    const handleDrop = useCallback((e: React.DragEvent) => {
        e.preventDefault();
        const f = e.dataTransfer.files[0];
        if (f) handleFileSelect(f);
    }, [handleFileSelect]);

    const handleProcess = async () => {
        if (!file) return;
        setIsProcessing(true);
        setError(null);
        setResults([]);

        const steps: ProgressStep[] = [
            { label: "Uploading file",             status: "active" },
            { label: "Detecting format",           status: "pending" },
            { label: "Extracting text layout",     status: "pending" },
            { label: "Parsing booth blocks",       status: "pending" },
            { label: "Complete",                   status: "pending" },
        ];
        setProgress([...steps]);

        try {
            const formData = new FormData();
            formData.append("file", file);

            const response = await fetch("/api/floorplan", { method: "POST", body: formData });
            if (!response.ok) throw new Error(`Processing failed: ${response.statusText}`);

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
                    if (!line.startsWith("data: ")) continue;
                    try {
                        const data = JSON.parse(line.slice(6));
                        if (data.type === "progress") {
                            const idx = data.step;
                            setProgress(steps.map((s, i) => ({
                                ...s,
                                label: i === idx ? (data.message || s.label) : s.label,
                                status: i < idx ? "done" : i === idx ? "active" : "pending",
                            }) as ProgressStep));
                        } else if (data.type === "result") {
                            setResults(data.rows || []);
                            setProgress(steps.map((s) => ({ ...s, status: "done" as const })));
                        } else if (data.type === "error") {
                            throw new Error(data.message);
                        }
                    } catch (e) {
                        if (e instanceof SyntaxError) continue;
                        throw e;
                    }
                }
            }
        } catch (err) {
            setError(err instanceof Error ? err.message : "Unknown error");
            setProgress((p) => p.map((s) => s.status === "active" ? { ...s, status: "error" as const } : s));
        } finally {
            setIsProcessing(false);
        }
    };

    const handleExport = async (format: "csv" | "excel" | "json") => {
        if (!results.length) return;
        try {
            const res = await fetch("/api/floorplan/export", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ rows: results, format }),
            });
            if (!res.ok) throw new Error("Export failed");
            const blob = await res.blob();
            const url = URL.createObjectURL(blob);
            const a = document.createElement("a");
            a.href = url;
            a.download = `floorplan-results.${format === "excel" ? "xlsx" : format}`;
            a.click();
            URL.revokeObjectURL(url);
        } catch {
            setError("Export failed. Please try again.");
        }
    };

    const filteredResults = results.filter((row) =>
        Object.values(row).some((v) => String(v ?? "").toLowerCase().includes(searchTerm.toLowerCase()))
    );

    const allKeys = results.length > 0 ? Object.keys(results[0]) : [];
    const columns = [
        ...PREFERRED_COLUMNS.filter((c) => allKeys.includes(c)),
        ...allKeys.filter((k) => !PREFERRED_COLUMNS.includes(k) && k !== "raw_text" && k !== "line_number"),
    ];

    const withExhibitor  = results.filter((r) => r.exhibitor_name?.trim()).length;
    const boothOnly      = results.filter((r) => !r.exhibitor_name?.trim()).length;
    const withDimensions = results.filter((r) => r.booth_size?.trim()).length;
    const withArea       = results.filter((r) => r.area_sqm?.trim()).length;

    return (
        <div className="min-h-screen py-10" style={{ background: "oklch(0.975 0.006 240)" }}>
            <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
                {/* Header */}
                <div className="flex items-center gap-3 mb-8">
                    <Link href="/dashboard">
                        <button className="flex items-center gap-1.5 text-sm text-muted-foreground hover:text-foreground transition-colors px-3 py-1.5 rounded-lg hover:bg-white border border-transparent hover:border-border">
                            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
                                <path d="M19 12H5" /><path d="M12 19l-7-7 7-7" />
                            </svg>
                            Dashboard
                        </button>
                    </Link>
                    <div className="h-4 w-px bg-border" />
                    <div>
                        <h1 className="text-xl font-bold text-foreground">Floor Plan Extractor</h1>
                        <p className="text-xs text-muted-foreground mt-0.5">Python OCR · Spatial block grouping · Smart filtering</p>
                    </div>
                </div>

                <div className="grid lg:grid-cols-[300px_1fr] gap-6">
                    {/* ── Left Panel ── */}
                    <div className="space-y-4">
                        {/* Upload Zone */}
                        <div
                            onDrop={handleDrop}
                            onDragOver={(e) => e.preventDefault()}
                            onClick={() => fileInputRef.current?.click()}
                            className={`relative rounded-xl border-2 border-dashed cursor-pointer transition-all duration-200 overflow-hidden group
                                ${file
                                    ? "border-primary/40 bg-primary/4"
                                    : "border-border hover:border-primary/30 hover:bg-white bg-white/60"
                                }`}
                        >
                            <input
                                ref={fileInputRef}
                                type="file"
                                accept=".pdf,.png,.jpg,.jpeg"
                                className="hidden"
                                onChange={(e) => { const f = e.target.files?.[0]; if (f) handleFileSelect(f); }}
                            />
                            {file ? (
                                <div className="p-6">
                                    {preview && (
                                        <img src={preview} alt="Preview" className="w-full h-36 object-contain rounded-lg mb-4 bg-accent" />
                                    )}
                                    <div className="flex items-start gap-3">
                                        <div className="w-8 h-8 rounded-lg bg-primary/10 flex items-center justify-center flex-shrink-0">
                                            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" className="text-primary">
                                                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
                                                <polyline points="14 2 14 8 20 8" />
                                            </svg>
                                        </div>
                                        <div className="min-w-0">
                                            <p className="text-sm font-semibold text-foreground truncate">{file.name}</p>
                                            <p className="text-xs text-muted-foreground mt-0.5">{(file.size / 1024 / 1024).toFixed(2)} MB · Click to change</p>
                                        </div>
                                    </div>
                                </div>
                            ) : (
                                <div className="p-10 text-center">
                                    <div className="w-12 h-12 rounded-xl bg-primary/8 border border-primary/15 flex items-center justify-center mx-auto mb-4 group-hover:scale-105 transition-transform">
                                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" className="text-primary">
                                            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                                            <polyline points="17 8 12 3 7 8" />
                                            <line x1="12" y1="3" x2="12" y2="15" />
                                        </svg>
                                    </div>
                                    <p className="text-sm font-semibold text-foreground mb-1">Drop your floor plan here</p>
                                    <p className="text-xs text-muted-foreground">PDF · PNG · JPG · JPEG</p>
                                </div>
                            )}
                        </div>

                        {/* Extract Button */}
                        <Button
                            onClick={handleProcess}
                            disabled={!file || isProcessing}
                            className="w-full bg-primary hover:bg-primary/90 text-primary-foreground font-semibold shadow-sm shadow-primary/15 h-10"
                        >
                            {isProcessing ? (
                                <span className="flex items-center gap-2">
                                    <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
                                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                                    </svg>
                                    Processing...
                                </span>
                            ) : (
                                <span className="flex items-center gap-2">
                                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
                                        <circle cx="11" cy="11" r="8" /><path d="m21 21-4.35-4.35" />
                                    </svg>
                                    Extract Booth Data
                                </span>
                            )}
                        </Button>

                        {/* Progress */}
                        {progress.length > 0 && (
                            <div className="card-elevated rounded-xl p-4">
                                <p className="text-[11px] font-bold text-muted-foreground uppercase tracking-wider mb-3">Progress</p>
                                <div className="space-y-2.5">
                                    {progress.map((step, i) => (
                                        <div key={i} className="flex items-center gap-3">
                                            <div className={`w-5 h-5 rounded-full flex items-center justify-center text-[10px] flex-shrink-0 transition-colors
                                                ${step.status === "done"  ? "bg-emerald-100 text-emerald-600 border border-emerald-200"
                                                : step.status === "active" ? "bg-primary/10 text-primary border border-primary/20 animate-pulse"
                                                : step.status === "error"  ? "bg-red-100 text-red-500 border border-red-200"
                                                : "bg-muted text-muted-foreground/40 border border-border"}`}>
                                                {step.status === "done" ? "✓" : step.status === "error" ? "✕" : i + 1}
                                            </div>
                                            <span className={`text-xs leading-tight ${
                                                step.status === "active" ? "text-foreground font-semibold"
                                                : step.status === "done"  ? "text-muted-foreground"
                                                : "text-muted-foreground/50"}`}>
                                                {step.label}
                                            </span>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}

                        {/* Error */}
                        {error && (
                            <div className="rounded-xl bg-red-50 border border-red-200 p-4">
                                <div className="flex gap-2">
                                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" className="text-red-500 flex-shrink-0 mt-0.5">
                                        <circle cx="12" cy="12" r="10" /><line x1="12" y1="8" x2="12" y2="12" /><line x1="12" y1="16" x2="12.01" y2="16" />
                                    </svg>
                                    <p className="text-sm text-red-600 leading-relaxed">{error}</p>
                                </div>
                            </div>
                        )}

                        {/* Tips */}
                        {!file && !isProcessing && (
                            <div className="rounded-xl bg-white border border-border p-4">
                                <p className="text-[11px] font-bold text-muted-foreground uppercase tracking-wider mb-2.5">What gets extracted</p>
                                <ul className="space-y-1.5">
                                    {[
                                        "Booth / stand number (any format)",
                                        "Exhibitor name — if shown",
                                        "Dimensions (e.g. 14X14 M)",
                                        "Area in m² (e.g. 196 sq.m.)",
                                        "Hall or pavilion name",
                                        "Toilets, entrances & corridors filtered out",
                                    ].map((tip) => (
                                        <li key={tip} className="flex items-start gap-2 text-xs text-muted-foreground">
                                            <span className="text-primary font-bold mt-0.5">·</span>
                                            {tip}
                                        </li>
                                    ))}
                                </ul>
                            </div>
                        )}
                    </div>

                    {/* ── Right Panel: Results ── */}
                    <div>
                        {results.length > 0 ? (
                            <div className="space-y-4">
                                {/* Stats */}
                                <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                                    {[
                                        { value: results.length, label: "Total Booths",    accent: "text-foreground" },
                                        { value: withExhibitor,  label: "With Exhibitor",  accent: "text-emerald-600" },
                                        { value: boothOnly,      label: "Booth Only",      accent: "text-amber-600" },
                                        { value: withDimensions, label: "With Dimensions", accent: "text-primary" },
                                    ].map((s) => (
                                        <div key={s.label} className="card-elevated rounded-xl p-4">
                                            <div className={`text-2xl font-bold tabular-nums ${s.accent}`}>{s.value}</div>
                                            <div className="text-xs text-muted-foreground mt-0.5">{s.label}</div>
                                        </div>
                                    ))}
                                </div>

                                {/* Search & Export */}
                                <div className="flex flex-col sm:flex-row gap-3 items-start sm:items-center justify-between">
                                    <div className="relative w-full sm:w-72">
                                        <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground">
                                            <circle cx="11" cy="11" r="8" /><path d="m21 21-4.35-4.35" />
                                        </svg>
                                        <input
                                            type="text"
                                            placeholder="Search booths, names..."
                                            value={searchTerm}
                                            onChange={(e) => setSearchTerm(e.target.value)}
                                            className="w-full pl-8 pr-3 py-2 text-sm rounded-lg bg-white border border-border focus:border-primary/50 focus:outline-none focus:ring-1 focus:ring-primary/20 transition-colors"
                                        />
                                    </div>
                                    <div className="flex items-center gap-2">
                                        <span className="text-xs text-muted-foreground hidden sm:block">Export:</span>
                                        {(["csv", "excel", "json"] as const).map((fmt) => (
                                            <Button
                                                key={fmt}
                                                variant="outline"
                                                size="sm"
                                                onClick={() => handleExport(fmt)}
                                                className="text-xs h-8 px-3 bg-white border-border hover:bg-accent hover:border-primary/25 font-medium"
                                            >
                                                {fmt.toUpperCase()}
                                            </Button>
                                        ))}
                                    </div>
                                </div>

                                <p className="text-xs text-muted-foreground">
                                    Showing <span className="font-semibold text-foreground">{filteredResults.length}</span> of{" "}
                                    <span className="font-semibold text-foreground">{results.length}</span> booths
                                    {withArea > 0 && <span> · {withArea} with area data</span>}
                                </p>

                                {/* Table */}
                                <div className="card-elevated rounded-xl overflow-hidden">
                                    <div className="overflow-x-auto">
                                        <table className="w-full text-sm">
                                            <thead>
                                                <tr className="border-b border-border bg-accent/60">
                                                    {columns.map((col) => (
                                                        <th key={col} className="text-left px-4 py-3 text-[11px] font-bold text-muted-foreground uppercase tracking-wider whitespace-nowrap">
                                                            {COLUMN_LABELS[col] ?? col.replace(/_/g, " ")}
                                                        </th>
                                                    ))}
                                                </tr>
                                            </thead>
                                            <tbody>
                                                {filteredResults.map((row, i) => {
                                                    const hasName = row.exhibitor_name?.trim();
                                                    return (
                                                        <tr key={i} className="border-b border-border/60 hover:bg-accent/40 transition-colors">
                                                            {columns.map((col) => {
                                                                const val = row[col];
                                                                const empty = val === undefined || val === null || val === "";

                                                                if (col === "booth_number") return (
                                                                    <td key={col} className="px-4 py-3 whitespace-nowrap">
                                                                        <span className="font-mono text-xs font-bold bg-primary/8 text-primary border border-primary/15 px-2 py-0.5 rounded-md">
                                                                            {String(val ?? "—")}
                                                                        </span>
                                                                    </td>
                                                                );

                                                                if (col === "exhibitor_name") return (
                                                                    <td key={col} className="px-4 py-3 whitespace-nowrap">
                                                                        {hasName
                                                                            ? <span className="font-semibold text-foreground">{String(val)}</span>
                                                                            : <span className="text-muted-foreground/50 text-xs italic">No name listed</span>
                                                                        }
                                                                    </td>
                                                                );

                                                                if (col === "source") return (
                                                                    <td key={col} className="px-4 py-3 whitespace-nowrap">
                                                                        <span className={`text-[10px] px-2 py-0.5 rounded-full font-semibold border
                                                                            ${val === "vector" ? "bg-blue-50 text-blue-600 border-blue-200"
                                                                            : val === "block"  ? "bg-emerald-50 text-emerald-600 border-emerald-200"
                                                                            : "bg-amber-50 text-amber-600 border-amber-200"
                                                                            }`}>
                                                                            {String(val ?? "—")}
                                                                        </span>
                                                                    </td>
                                                                );

                                                                return (
                                                                    <td key={col} className={`px-4 py-3 whitespace-nowrap ${empty ? "text-muted-foreground/30 text-xs" : "text-foreground"}`}>
                                                                        {empty ? "—" : String(val)}
                                                                    </td>
                                                                );
                                                            })}
                                                        </tr>
                                                    );
                                                })}
                                            </tbody>
                                        </table>
                                    </div>
                                    {filteredResults.length === 0 && searchTerm && (
                                        <div className="py-12 text-center">
                                            <p className="text-sm text-muted-foreground">No booths match &quot;{searchTerm}&quot;</p>
                                        </div>
                                    )}
                                </div>
                            </div>
                        ) : (
                            <div className="card-elevated rounded-2xl p-16 text-center flex flex-col items-center justify-center min-h-[420px]">
                                <div className="w-16 h-16 rounded-2xl bg-primary/8 border border-primary/15 flex items-center justify-center mx-auto mb-6">
                                    <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" className="text-primary/70">
                                        <rect x="2" y="2" width="20" height="20" rx="2" />
                                        <path d="M2 8h20" />
                                        <path d="M8 2v20" />
                                        <path d="M14 14h4" />
                                        <path d="M14 17h2" />
                                    </svg>
                                </div>
                                <h3 className="text-base font-bold text-foreground mb-2">Ready to Extract</h3>
                                <p className="text-sm text-muted-foreground max-w-xs mx-auto leading-relaxed">
                                    Upload a floor plan and click <span className="text-foreground font-semibold">Extract Booth Data</span>.
                                    Spatial OCR will identify all booths, numbers, dimensions and area.
                                </p>
                                <div className="mt-8 flex flex-wrap gap-2 justify-center">
                                    {["Booth Numbers", "Exhibitor Names", "Dimensions", "Area m²", "Hall Info"].map((tag) => (
                                        <span key={tag} className="tag-blue text-xs px-2.5 py-1 rounded-full font-medium">{tag}</span>
                                    ))}
                                </div>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
}
