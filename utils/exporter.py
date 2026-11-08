"""
Report Exporter Utility
Generates CSV and multi-sheet formatted Excel (.xlsx) workbooks for telemetry,
fault analysis, channel comparisons, and AI evaluation metrics.
"""

import io
import pandas as pd
import openpyxl
from openpyxl.styles import PatternFill, Font, Alignment, Border, Side


def generate_csv(df: pd.DataFrame) -> bytes:
    """Converts a pandas DataFrame to CSV bytes."""
    return df.to_csv(index=False).encode("utf-8")


def generate_excel_report(report_name: str, sheets_data: dict) -> bytes:
    """
    Generates an Excel workbook with custom styling, headers, and multiple sheets.
    sheets_data is a dict of { 'Sheet Name': pandas.DataFrame }.
    Returns bytes of the resulting Excel file.
    """
    wb = openpyxl.Workbook()
    # Remove default active sheet
    wb.remove(wb.active)

    header_fill = PatternFill(start_color="0F172A", end_color="0F172A", fill_type="solid")
    header_font = Font(name="Segoe UI", size=11, bold=True, color="00F2FE")
    border_style = Side(border_style="thin", color="1E3A8A")
    cell_border = Border(left=border_style, right=border_style, top=border_style, bottom=border_style)

    for sheet_name, df in sheets_data.items():
        ws = wb.create_sheet(title=sheet_name[:31])  # Excel sheet title limit is 31 chars
        
        # Write Title Header
        ws.cell(row=1, column=1, value=f"AI DIGITAL SIGNAL MONITORING SYSTEM — {report_name.upper()}")
        ws.cell(row=1, column=1).font = Font(name="Segoe UI", size=13, bold=True, color="0066FF")
        ws.cell(row=2, column=1, value=f"Exported at: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')} | Data Mode: SIMULATED BENCHMARK DATA")
        ws.cell(row=2, column=1).font = Font(name="Segoe UI", size=9, italic=True, color="64748B")

        # Write Table Headers at row 4
        start_row = 4
        headers = list(df.columns)
        for col_idx, header in enumerate(headers, 1):
            cell = ws.cell(row=start_row, column=col_idx, value=str(header).replace("_", " ").title())
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal="center", vertical="center")
            cell.border = cell_border

        # Write Data Rows
        for row_idx, row_data in enumerate(df.values, start_row + 1):
            for col_idx, val in enumerate(row_data, 1):
                cell = ws.cell(row=row_idx, column=col_idx, value=val)
                cell.font = Font(name="Segoe UI", size=10)
                cell.border = cell_border
                cell.alignment = Alignment(horizontal="left", vertical="center")

        # Auto-adjust column widths
        for col in ws.columns:
            max_len = max(len(str(cell.value or "")) for cell in col)
            col_letter = openpyxl.utils.get_column_letter(col[0].column)
            ws.column_dimensions[col_letter].width = max(max_len + 3, 12)

    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    return output.getvalue()

