const PYTHON_API_URL = process.env.PYTHON_API_URL || "http://localhost:8000";

export async function POST(request: Request) {
    try {
        const body = await request.json();

        const response = await fetch(`${PYTHON_API_URL}/api/scraper/analyze`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(body),
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({ detail: "Analysis failed" }));
            return new Response(
                JSON.stringify({ error: errorData.detail || "Analysis failed" }),
                { status: response.status, headers: { "Content-Type": "application/json" } }
            );
        }

        const data = await response.json();
        return new Response(JSON.stringify(data), {
            headers: { "Content-Type": "application/json" },
        });
    } catch (error) {
        console.error("Scraper analyze API error:", error);
        return new Response(
            JSON.stringify({
                error: "Failed to connect to processing server. Make sure the Python server is running on port 8000.",
            }),
            { status: 502, headers: { "Content-Type": "application/json" } }
        );
    }
}
