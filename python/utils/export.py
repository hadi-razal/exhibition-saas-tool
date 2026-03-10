"""
Export utilities — CSV, Excel, and JSON export helpers.
"""
import io
import json
import logging

import pandas as pd

logger = logging.getLogger("exhibitiq.utils.export")


def export_to_csv(rows: list[dict]) -> bytes:
    """Export rows to CSV format."""
    df = pd.DataFrame(rows)
    buffer = io.BytesIO()
    df.to_csv(buffer, index=False, encoding="utf-8-sig")
    buffer.seek(0)
    return buffer.getvalue()


def export_to_excel(rows: list[dict]) -> bytes:
    """Export rows to Excel format with clean formatting."""
    df = pd.DataFrame(rows)
    buffer = io.BytesIO()

    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Results")

        # Auto-adjust column widths
        worksheet = writer.sheets["Results"]
        for i, col in enumerate(df.columns):
            max_len = max(
                df[col].astype(str).map(len).max() if len(df) > 0 else 0,
                len(str(col)),
            )
            worksheet.column_dimensions[
                chr(65 + i) if i < 26 else chr(64 + i // 26) + chr(65 + i % 26)
            ].width = min(max_len + 2, 50)

    buffer.seek(0)
    return buffer.getvalue()


def export_to_json(rows: list[dict]) -> bytes:
    """Export rows to JSON format."""
    return json.dumps(rows, indent=2, ensure_ascii=False).encode("utf-8")
