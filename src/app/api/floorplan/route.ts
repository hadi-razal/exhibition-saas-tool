const PYTHON_API_URL = process.env.PYTHON_API_URL || "http://localhost:8000";

export async function POST(request: Request) {
    try {
        const formData = await request.formData();

        const response = await fetch(`${PYTHON_API_URL}/api/floorplan/extract`, {
            method: "POST",
            body: formData,
        });

        if (!response.ok) {
            const errorText = await response.text();
            return new Response(JSON.stringify({ error: errorText }), {
                status: response.status,
                headers: { "Content-Type": "application/json" },
            });
        }

        // Stream SSE from Python to client
        return new Response(response.body, {
            headers: {
                "Content-Type": "text/event-stream",
                "Cache-Control": "no-cache",
                Connection: "keep-alive",
            },
        });
    } catch (error) {
        console.error("Floor plan API error:", error);
        return new Response(
            JSON.stringify({
                error: "Failed to connect to processing server. Make sure the Python server is running on port 8000.",
            }),
            { status: 502, headers: { "Content-Type": "application/json" } }
        );
    }
}
