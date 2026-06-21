from __future__ import annotations

import base64
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen


README = Path(__file__).resolve().parents[1] / "README.md"
START_MARKER = "<!-- HACKATIME_START -->"
END_MARKER = "<!-- HACKATIME_END -->"


def fetch_month_seconds(api_key: str) -> int:
    now = datetime.now(timezone.utc)
    start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    query = urlencode(
        {
            "start_time": start.isoformat().replace("+00:00", "Z"),
            "end_time": now.isoformat().replace("+00:00", "Z"),
        }
    )
    request = Request(
        f"https://hackatime.hackclub.com/api/v1/my/heartbeats?{query}",
        headers={
            "Authorization": "Basic "
            + base64.b64encode(api_key.encode()).decode(),
            "Accept": "application/json",
            "User-Agent": "SansarKarki-profile-readme",
        },
    )
    with urlopen(request, timeout=30) as response:
        payload = json.load(response)
    return int(payload["total_seconds"])


def main() -> None:
    api_key = os.environ.get("HACKATIME_API_KEY", "").strip()
    if not api_key:
        raise SystemExit("HACKATIME_API_KEY is required")

    total_seconds = fetch_month_seconds(api_key)
    minutes = total_seconds // 60
    updated = datetime.now(timezone.utc).strftime("%B %-d, %Y at %H:%M UTC")
    replacement = (
        f"{START_MARKER}\n"
        f"**{minutes:,} minutes coded this month and counting.**  \n"
        f"<sub>Last refreshed {updated} from Hackatime.</sub>\n"
        f"{END_MARKER}"
    )

    original = README.read_text()
    updated_readme, count = re.subn(
        rf"{re.escape(START_MARKER)}.*?{re.escape(END_MARKER)}",
        replacement,
        original,
        flags=re.DOTALL,
    )
    if count != 1:
        raise SystemExit("Hackatime markers are missing or duplicated")
    README.write_text(updated_readme)


if __name__ == "__main__":
    main()
