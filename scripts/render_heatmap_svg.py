#!/usr/bin/env python3
"""
render_heatmap_svg.py
Reads data/contributions.json and renders a self-contained, animated contrib-heatmap.svg
following the Avi Vashishta-inspired terminal aesthetic.
"""

import json
import os
from datetime import datetime

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FILE = os.path.join(ROOT_DIR, "data", "contributions.json")
SVG_OUTPUT_FILE = os.path.join(ROOT_DIR, "contrib-heatmap.svg")

# Color ramp specified in design requirements
COLOR_RAMP = [
    "#161b22",  # Level 0 (empty)
    "#0e4429",  # Level 1
    "#006d32",  # Level 2
    "#26a641",  # Level 3
    "#39d353",  # Level 4
    "#69f0a0",  # Level 5 (peak contributions)
]

WIDTH = 860
HEIGHT = 156
CELL_SIZE = 11
CELL_GAP = 3.5
CELL_STEP = CELL_SIZE + CELL_GAP  # 14.5px
GRID_X = 42
GRID_Y = 26
RX = 2
RY = 2


def render_heatmap():
    if not os.path.exists(DATA_FILE):
        raise FileNotFoundError(f"{DATA_FILE} not found. Run fetch_contributions.py first.")

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    days = data.get("days", [])
    total_contributions = data.get("total_contributions", 0)

    # Map days by (col, row)
    grid = {}
    month_positions = {}
    last_month = None

    for d in days:
        col = d.get("col")
        row = d.get("row")
        date_str = d.get("date")

        if col is not None and row is not None:
            grid[(col, row)] = d

            # Detect month changes to position month labels
            if date_str:
                dt = datetime.strptime(date_str, "%Y-%m-%d")
                m_name = dt.strftime("%b")
                if m_name != last_month and col not in month_positions:
                    # Only add if not too close to another label
                    if not month_positions or (col - max(month_positions.keys())) >= 3:
                        month_positions[col] = m_name
                    last_month = m_name

    # Determine max columns (usually 53)
    max_col = max((d.get("col", 0) for d in days), default=52)
    num_cols = max(53, max_col + 1)

    # Build SVG content
    svg_parts = []
    svg_parts.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {HEIGHT}" width="{WIDTH}" height="{HEIGHT}">')
    svg_parts.append("""  <defs>
    <style>
      .bg { fill: #0d1117; }
      .lbl { font-family: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, "Liberation Mono", monospace; font-size: 10px; fill: #7d8590; }
      .stat-lbl { font-family: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, "Liberation Mono", monospace; font-size: 11px; fill: #8b949e; font-weight: 500; }
      .stat-highlight { fill: #38bdf8; font-weight: 600; }
      .cell {
        transform-box: fill-box;
        transform-origin: center;
        opacity: 0.2;
        transform: scale(0.6);
        animation: diagonalWipe 0.45s cubic-bezier(0.16, 1, 0.3, 1) forwards;
      }
      @keyframes diagonalWipe {
        to {
          opacity: 1;
          transform: scale(1);
        }
      }
    </style>
  </defs>""")

    # Background canvas
    svg_parts.append(f'  <rect width="{WIDTH}" height="{HEIGHT}" class="bg" rx="8" ry="8" />')

    # Month Labels (Top)
    for col_idx, m_name in sorted(month_positions.items()):
        x_pos = GRID_X + (col_idx * CELL_STEP)
        svg_parts.append(f'  <text x="{x_pos:.1f}" y="{GRID_Y - 10}" class="lbl">{m_name}</text>')

    # Day Labels (Left) - Mon, Wed, Fri
    day_labels = [(1, "Mon"), (3, "Wed"), (5, "Fri")]
    for r_idx, label in day_labels:
        y_pos = GRID_Y + (r_idx * CELL_STEP) + (CELL_SIZE - 2)
        svg_parts.append(f'  <text x="14" y="{y_pos:.1f}" class="lbl">{label}</text>')

    # Heatmap Cells
    for c in range(num_cols):
        for r in range(7):
            d = grid.get((c, r))
            if not d:
                # Cell outside the active 365-day range
                continue

            count = d.get("count", 0)
            level = d.get("level", 0)

            # Assign color from ramp
            if level == 0 or count == 0:
                color = COLOR_RAMP[0]
            elif level == 1:
                color = COLOR_RAMP[1]
            elif level == 2:
                color = COLOR_RAMP[2]
            elif level == 3:
                color = COLOR_RAMP[3]
            elif level == 4:
                color = COLOR_RAMP[5] if count >= 15 else COLOR_RAMP[4]
            else:
                color = COLOR_RAMP[4]

            x_pos = GRID_X + (c * CELL_STEP)
            y_pos = GRID_Y + (r * CELL_STEP)

            # Diagonal coordinate for stagger animation: (col + row) * 8ms
            delay_ms = (c + r) * 8

            date_str = d.get("date", "")
            title_text = f"{count} contribution{'s' if count != 1 else ''} on {date_str}"

            svg_parts.append(
                f'  <rect class="cell" x="{x_pos:.1f}" y="{y_pos:.1f}" '
                f'width="{CELL_SIZE}" height="{CELL_SIZE}" rx="{RX}" ry="{RY}" fill="{color}" '
                f'style="animation-delay: {delay_ms}ms;">'
                f'<title>{title_text}</title>'
                f'</rect>'
            )

    # Footer (Summary Counter + Legend)
    footer_y = GRID_Y + (7 * CELL_STEP) + 14

    # Left: Total Contributions Counter
    svg_parts.append(
        f'  <text x="{GRID_X}" y="{footer_y}" class="stat-lbl">'
        f'<tspan class="stat-highlight">{total_contributions:,}</tspan> contributions in the last year'
        f'</text>'
    )

    # Right: "Less" [color squares] "More" Legend
    legend_right_x = GRID_X + (num_cols * CELL_STEP) - CELL_GAP
    legend_step_w = 11
    legend_gap = 3.5
    legend_colors = [COLOR_RAMP[0], COLOR_RAMP[1], COLOR_RAMP[2], COLOR_RAMP[3], COLOR_RAMP[4]]
    legend_total_cells_w = (len(legend_colors) * (legend_step_w + legend_gap)) - legend_gap

    # "More" text
    more_x = legend_right_x
    svg_parts.append(f'  <text x="{more_x}" y="{footer_y - 1}" class="lbl" text-anchor="end">More</text>')

    # Calculate starting X for legend squares
    more_text_width = 32
    squares_end_x = more_x - more_text_width
    squares_start_x = squares_end_x - legend_total_cells_w

    # "Less" text
    less_x = squares_start_x - 8
    svg_parts.append(f'  <text x="{less_x}" y="{footer_y - 1}" class="lbl" text-anchor="end">Less</text>')

    # Draw legend squares
    for i, colr in enumerate(legend_colors):
        sq_x = squares_start_x + (i * (legend_step_w + legend_gap))
        sq_y = footer_y - 10
        svg_parts.append(
            f'  <rect x="{sq_x:.1f}" y="{sq_y:.1f}" width="{legend_step_w}" height="{legend_step_w}" '
            f'rx="{RX}" ry="{RY}" fill="{colr}" />'
        )

    svg_parts.append('</svg>\n')

    full_svg = "\n".join(svg_parts)
    with open(SVG_OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(full_svg)

    print(f"Generated {SVG_OUTPUT_FILE} ({len(full_svg)} bytes).")


if __name__ == "__main__":
    render_heatmap()
