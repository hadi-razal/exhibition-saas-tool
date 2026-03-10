"use client";

import { useState, useCallback, useRef } from "react";
import { Button } from "@/components/ui/button";
import Link from "next/link";

interface ExtractedRow {
    page?: number;
    booth_number?: string;
    exhibitor_name?: string;
    booth_size?: string;
    hall?: string;
    zone?: string;
    raw_text?: string;
    confidence?: string;
    [key: string]: string | number | undefined;
}

interface ProgressStep {
    label: string;
    status: "pending" | "active" | "done" | "error";
}

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

        // Create preview for images
        if (selectedFile.type.startsWith("image/")) {
            const reader = new FileReader();
            reader.onload = (e) => setPreview(e.target?.result as string);
            reader.readAsDataURL(selectedFile);
        } else {
            setPreview(null);
        }
    }, []);

    const handleDrop = useCallback(
        (e: React.DragEvent) => {
            e.preventDefault();
            const droppedFile = e.dataTransfer.files[0];
            if (droppedFile) handleFileSelect(droppedFile);
        },
        [handleFileSelect]
    );

    const handleProcess = async () => {
        if (!file) return;

        setIsProcessing(true);
        setError(null);
        setResults([]);

        const steps: ProgressStep[] = [
            { label: "Uploading file", status: "active" },
            { label: "Detecting format", status: "pending" },
            { label: "Extracting text / Running OCR", status: "pending" },
            { label: "Parsing structured data", status: "pending" },
            { label: "Complete", status: "pending" },
        ];
        setProgress([...steps]);

        try {
            const formData = new FormData();
            formData.append("file", file);

            const response = await fetch("/api/floorplan", {
                method: "POST",
                body: formData,
            });

            if (!response.ok) {
                throw new Error(`Processing failed: ${response.statusText}`);
            }

            // Handle SSE stream
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
                                const stepIndex = data.step;
                                const newSteps = steps.map((s, i) => ({
                                    ...s,
                                    status:
                                        i < stepIndex ? "done" as const :
                                            i === stepIndex ? "active" as const :
                                                "pending" as const,
                                }));
                                setProgress(newSteps);
                            } else if (data.type === "result") {
                                setResults(data.rows || []);
                                const finalSteps = steps.map((s) => ({ ...s, status: "done" as const }));
                                setProgress(finalSteps);
                            } else if (data.type === "error") {
                                throw new Error(data.message);
                            }
                        } catch (parseError) {
                            // Skip non-JSON lines
                            if (parseError instanceof SyntaxError) continue;
                            throw parseError;
                        }
                    }
                }
            }
        } catch (err) {
            setError(err instanceof Error ? err.message : "An unknown error occurred");
            setProgress((prev) =>
                prev.map((s) => (s.status === "active" ? { ...s, status: "error" as const } : s))
            );
        } finally {
            setIsProcessing(false);
        }
    };

    const handleExport = async (format: "csv" | "excel" | "json") => {
        if (results.length === 0) return;

        try {
            const response = await fetch("/api/floorplan/export", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ rows: results, format }),
            });

            if (!response.ok) throw new Error("Export failed");

            const blob = await response.blob();
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
        Object.values(row).some((val) =>
            String(val).toLowerCase().includes(searchTerm.toLowerCase())
        )
    );

    const columns = results.length > 0
        ? Object.keys(results[0]).filter((k) => k !== "raw_text")
        : [];

    // Summary stats
    const uniqueBooths = new Set(results.map((r) => r.booth_number).filter(Boolean)).size;
    const uniqueExhibitors = new Set(results.map((r) => r.exhibitor_name).filter(Boolean)).size;
    const sizeEntries = results.filter((r) => r.booth_size).length;

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
                        <h1 className="text-2xl font-bold">Floor Plan OCR Extractor</h1>
                        <p className="text-sm text-muted-foreground">Upload a floor plan and extract structured booth data</p>
                    </div>
                </div>

                <div className="grid lg:grid-cols-3 gap-6">
                    {/* Left: Upload & Progress */}
                    <div className="lg:col-span-1 space-y-6">
                        {/* Upload Area */}
                        <div
                            onDrop={handleDrop}
                            onDragOver={(e) => e.preventDefault()}
                            onClick={() => fileInputRef.current?.click()}
                            className={`glass-card rounded-xl p-8 text-center cursor-pointer transition-all duration-200 ${file
                                    ? "border-primary/30"
                                    : "border-dashed border-2 border-border hover:border-primary/30"
                                }`}
                        >
                            <input
                                ref={fileInputRef}
                                type="file"
                                accept=".pdf,.png,.jpg,.jpeg"
                                className="hidden"
                                onChange={(e) => {
                                    const f = e.target.files?.[0];
                                    if (f) handleFileSelect(f);
                                }}
                            />

                            {file ? (
                                <div>
                                    {preview && (
                                        <img
                                            src={preview}
                                            alt="Preview"
                                            className="w-full h-40 object-contain rounded-lg mb-4 bg-card"
                                        />
                                    )}
                                    <div className="flex items-center gap-2 justify-center mb-2">
                                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" className="text-primary">
                                            <polyline points="20 6 9 17 4 12" />
                                        </svg>
                                        <span className="text-sm font-medium">{file.name}</span>
                                    </div>
                                    <p className="text-xs text-muted-foreground">
                                        {(file.size / 1024 / 1024).toFixed(2)} MB • Click to change
                                    </p>
                                </div>
                            ) : (
                                <div>
                                    <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" className="text-muted-foreground mx-auto mb-4">
                                        <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                                        <polyline points="17 8 12 3 7 8" />
                                        <line x1="12" y1="3" x2="12" y2="15" />
                                    </svg>
                                    <p className="text-sm font-medium mb-1">Drop your floor plan here</p>
                                    <p className="text-xs text-muted-foreground">PDF, PNG, JPG, JPEG</p>
                                </div>
                            )}
                        </div>

                        {/* Process Button */}
                        <Button
                            onClick={handleProcess}
                            disabled={!file || isProcessing}
                            className="w-full bg-primary hover:bg-primary/90 text-primary-foreground shadow-lg shadow-primary/25"
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
                                "Extract Data →"
                            )}
                        </Button>

                        {/* Progress Steps */}
                        {progress.length > 0 && (
                            <div className="glass-card rounded-xl p-5">
                                <h3 className="text-sm font-semibold mb-4">Progress</h3>
                                <div className="space-y-3">
                                    {progress.map((step, i) => (
                                        <div key={i} className="flex items-center gap-3">
                                            <div className={`w-6 h-6 rounded-full flex items-center justify-center text-xs flex-shrink-0 ${step.status === "done"
                                                    ? "bg-green-500/20 text-green-400"
                                                    : step.status === "active"
                                                        ? "bg-primary/20 text-primary animate-pulse"
                                                        : step.status === "error"
                                                            ? "bg-destructive/20 text-destructive"
                                                            : "bg-muted text-muted-foreground"
                                                }`}>
                                                {step.status === "done" ? "✓" : step.status === "error" ? "✕" : i + 1}
                                            </div>
                                            <span className={`text-sm ${step.status === "active" ? "text-foreground font-medium" : "text-muted-foreground"
                                                }`}>
                                                {step.label}
                                            </span>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}

                        {/* Error */}
                        {error && (
                            <div className="rounded-xl bg-destructive/10 border border-destructive/20 p-4">
                                <p className="text-sm text-destructive">{error}</p>
                            </div>
                        )}
                    </div>

                    {/* Right: Results */}
                    <div className="lg:col-span-2">
                        {results.length > 0 ? (
                            <div className="space-y-6">
                                {/* Summary Cards */}
                                <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                                    <div className="glass-card rounded-lg p-4">
                                        <div className="text-2xl font-bold">{results.length}</div>
                                        <div className="text-xs text-muted-foreground">Total Rows</div>
                                    </div>
                                    <div className="glass-card rounded-lg p-4">
                                        <div className="text-2xl font-bold">{uniqueBooths}</div>
                                        <div className="text-xs text-muted-foreground">Unique Booths</div>
                                    </div>
                                    <div className="glass-card rounded-lg p-4">
                                        <div className="text-2xl font-bold">{uniqueExhibitors}</div>
                                        <div className="text-xs text-muted-foreground">Exhibitor Names</div>
                                    </div>
                                    <div className="glass-card rounded-lg p-4">
                                        <div className="text-2xl font-bold">{sizeEntries}</div>
                                        <div className="text-xs text-muted-foreground">Size Values</div>
                                    </div>
                                </div>

                                {/* Search & Export */}
                                <div className="flex flex-col sm:flex-row gap-3 items-start sm:items-center justify-between">
                                    <input
                                        type="text"
                                        placeholder="Search results..."
                                        value={searchTerm}
                                        onChange={(e) => setSearchTerm(e.target.value)}
                                        className="w-full sm:w-64 px-3 py-2 text-sm rounded-lg bg-input border border-border/50 focus:border-primary/50 focus:outline-none"
                                    />
                                    <div className="flex gap-2">
                                        <Button variant="outline" size="sm" onClick={() => handleExport("csv")}>
                                            CSV
                                        </Button>
                                        <Button variant="outline" size="sm" onClick={() => handleExport("excel")}>
                                            Excel
                                        </Button>
                                        <Button variant="outline" size="sm" onClick={() => handleExport("json")}>
                                            JSON
                                        </Button>
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
                                                            <td key={col} className="px-4 py-3 whitespace-nowrap">
                                                                {String(row[col] ?? "—")}
                                                            </td>
                                                        ))}
                                                    </tr>
                                                ))}
                                            </tbody>
                                        </table>
                                    </div>
                                </div>
                            </div>
                        ) : (
                            /* Empty State */
                            <div className="glass-card rounded-2xl p-16 text-center">
                                <svg width="60" height="60" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1" strokeLinecap="round" strokeLinejoin="round" className="text-muted-foreground/30 mx-auto mb-6">
                                    <rect x="2" y="2" width="20" height="20" rx="2" />
                                    <path d="M2 8h20" />
                                    <path d="M8 2v20" />
                                </svg>
                                <h3 className="text-lg font-semibold mb-2 text-muted-foreground">No Results Yet</h3>
                                <p className="text-sm text-muted-foreground/70 max-w-sm mx-auto">
                                    Upload a floor plan file and click &quot;Extract Data&quot; to see structured booth data here.
                                </p>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
}
