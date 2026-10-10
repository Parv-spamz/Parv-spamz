#!/usr/bin/env python3
"""
fetch_contributions.py
Scrapes GitHub contribution data for Parv-spamz and saves parsed metrics to data/contributions.json.
"""

import json
import os
import re
from datetime import datetime, timezone
import requests
from bs4 import BeautifulSoup

USERNAME = "Parv-spamz"
CONTRIBUTIONS_URL = f"https://github.com/users/{USERNAME}/contributions"
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "contributions.json")


def fetch_contributions():
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    }

    response = requests.get(CONTRIBUTIONS_URL, headers=headers, timeout=15)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    # 1. Parse Total Contributions from Header
    total_contributions = 0
    for header in soup.find_all(["h2", "h3"]):
        text = header.get_text(" ", strip=True)
        match = re.search(r"([\d,]+)\s+contributions?\s+in\s+the\s+last\s+year", text, re.IGNORECASE)
        if match:
            total_contributions = int(match.group(1).replace(",", ""))
            break

    # 2. Build Tooltip Lookup
    tooltips = {}
    for tt in soup.find_all("tool-tip"):
        target_id = tt.get("for")
        if target_id:
            tooltips[target_id] = tt.get_text(" ", strip=True)

    # 3. Parse Calendar Days
    day_elements = soup.find_all("td", class_="ContributionCalendar-day")
    parsed_days = []

    for td in day_elements:
        date_str = td.get("data-date")
        if not date_str:
            continue

        level_str = td.get("data-level", "0")
        try:
            level = int(level_str)
        except ValueError:
            level = 0

        elem_id = td.get("id", "")
        # Parse row and col from id: contribution-day-component-{row}-{col}
        col = None
        row = None
        id_match = re.search(r"contribution-day-component-(\d+)-(\d+)", elem_id)
        if id_match:
            row = int(id_match.group(1))
            col = int(id_match.group(2))
        else:
            ix = td.get("data-ix")
            if ix is not None:
                col = int(ix)

        # Extract contribution count from tooltip
        count = 0
        tt_text = tooltips.get(elem_id, "")
        if tt_text:
            if tt_text.lower().startswith("no contribution"):
                count = 0
            else:
                count_match = re.search(r"(\d+)\s+contribution", tt_text, re.IGNORECASE)
                if count_match:
                    count = int(count_match.group(1))
                elif level > 0:
                    count = level
        elif level > 0:
            count = level

        parsed_days.append({
            "date": date_str,
            "count": count,
            "level": level,
            "col": col,
            "row": row,
        })

    # Sort days chronologically
    parsed_days.sort(key=lambda d: d["date"])

    # Fallback if total_contributions wasn't parsed from header
    calc_total = sum(d["count"] for d in parsed_days)
    if total_contributions == 0:
        total_contributions = calc_total
    else:
        total_contributions = max(total_contributions, calc_total)

    # 4. Calculate Streaks
    current_streak = 0
    longest_streak = 0
    current_run = 0

    for day in parsed_days:
        if day["count"] > 0:
            current_run += 1
            if current_run > longest_streak:
                longest_streak = current_run
        else:
            current_run = 0

    # Current streak calculation (counting backwards from end)
    idx = len(parsed_days) - 1
    if idx >= 0 and parsed_days[idx]["count"] == 0:
        # Check if yesterday had contributions (in case today hasn't happened yet)
        idx -= 1

    while idx >= 0 and parsed_days[idx]["count"] > 0:
        current_streak += 1
        idx -= 1

    result = {
        "username": USERNAME,
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "total_contributions": total_contributions,
        "current_streak": current_streak,
        "longest_streak": longest_streak,
        "days_count": len(parsed_days),
        "days": parsed_days,
    }

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

    print(f"Successfully scraped {len(parsed_days)} days for {USERNAME}.")
    print(f"Total Contributions: {total_contributions} | Current Streak: {current_streak} | Longest Streak: {longest_streak}")
    print(f"Saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    fetch_contributions()
