const PYTHON_API_URL = process.env.PYTHON_API_URL || "http://localhost:8000";

export async function POST(request: Request) {
    try {
        const body = await request.json();

        const response = await fetch(`${PYTHON_API_URL}/api/floorplan/export`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(body),
        });

        if (!response.ok) {
            return new Response(JSON.stringify({ error: "Export failed" }), {
                status: response.status,
                headers: { "Content-Type": "application/json" },
            });
        }

        const contentType = response.headers.get("Content-Type") || "application/octet-stream";
        const contentDisposition = response.headers.get("Content-Disposition") || "";

        return new Response(response.body, {
            headers: {
                "Content-Type": contentType,
                "Content-Disposition": contentDisposition,
            },
        });
    } catch (error) {
        console.error("Export API error:", error);
        return new Response(
            JSON.stringify({ error: "Export failed" }),
            { status: 502, headers: { "Content-Type": "application/json" } }
        );
    }
}
