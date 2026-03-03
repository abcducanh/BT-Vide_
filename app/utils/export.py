import io
from openpyxl import Workbook

def rows_to_excel_bytes(headers: list[str], rows: list[list], sheet_name: str = "data") -> io.BytesIO:
    """Create an .xlsx in memory using openpyxl."""
    wb = Workbook()
    ws = wb.active
    ws.title = sheet_name

    ws.append(headers)
    for r in rows:
        ws.append(r)

    # simple auto width
    for col in ws.columns:
        max_len = 0
        col_letter = col[0].column_letter
        for cell in col:
            try:
                v = "" if cell.value is None else str(cell.value)
                if len(v) > max_len:
                    max_len = len(v)
            except Exception:
                pass
        ws.column_dimensions[col_letter].width = min(max(10, max_len + 2), 60)

    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    return buf
