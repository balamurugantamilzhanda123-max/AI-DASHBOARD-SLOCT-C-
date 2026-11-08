"""
Formatting Utilities for Communication Signals and Telemetry
"""

import math


def format_ber(val: float) -> str:
    """Formats Bit Error Rate into readable scientific / engineering string."""
    if val is None or math.isnan(val) or val <= 0:
        return "0.00"
    if val < 1e-6:
        return f"{val:.2e}"
    if val < 1e-2:
        return f"{val:.3e}"
    return f"{val:.4f}"


def format_number(val: int or float) -> str:
    """Formats numbers with comma separators."""
    if val is None:
        return "0"
    if isinstance(val, int):
        return f"{val:,}"
    return f"{val:,.2f}"


def get_severity_badge_html(severity: str) -> str:
    """Returns HTML markup for severity badges."""
    sev = str(severity).upper()
    if sev == "CRITICAL":
        return f'<span class="badge badge-critical"><span class="pulse-dot pulse-red"></span> CRITICAL</span>'
    elif sev in ["WARNING", "MEDIUM", "HIGH"]:
        return f'<span class="badge badge-warning"><span class="pulse-dot pulse-amber"></span> {sev}</span>'
    elif sev in ["OPTIMAL", "NORMAL", "HEALTHY", "RESOLVED"]:
        return f'<span class="badge badge-normal"><span class="pulse-dot pulse-green"></span> {sev}</span>'
    else:
        return f'<span class="badge badge-info"><span class="pulse-dot pulse-cyan"></span> {sev}</span>'


def get_channel_badge_html(channel: str) -> str:
    """Returns HTML tag for channel identifiers."""
    colors = {
        "CH1": "rgba(0, 242, 254, 0.15)",
        "CH2": "rgba(0, 102, 255, 0.15)",
        "CH3": "rgba(168, 85, 247, 0.15)"
    }
    borders = {
        "CH1": "rgba(0, 242, 254, 0.5)",
        "CH2": "rgba(0, 102, 255, 0.5)",
        "CH3": "rgba(168, 85, 247, 0.5)"
    }
    bg = colors.get(channel, "rgba(255, 255, 255, 0.1)")
    border = borders.get(channel, "rgba(255, 255, 255, 0.3)")
    return f'<span style="background:{bg}; border:1px solid {border}; color:#ffffff; padding:2px 8px; border-radius:4px; font-weight:600; font-family:monospace;">{channel}</span>'

