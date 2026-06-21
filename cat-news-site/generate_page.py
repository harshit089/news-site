"""
Generates a static HTML archive page (docs/index.html) for GitHub Pages,
showing today's digest plus a history of recent days.
"""
import json
import os

DOCS_DIR = "docs"
ARCHIVE_JSON = os.path.join(DOCS_DIR, "archive.json")
MAX_DAYS_KEPT = 30

CATEGORY_COLOR = {
    "Geopolitics": "#2563eb",
    "Economy": "#059669",
    "India National": "#ea580c",
}


def load_archive() -> list[dict]:
    if not os.path.exists(ARCHIVE_JSON):
        return []
    with open(ARCHIVE_JSON, "r", encoding="utf-8") as f:
        return json.load(f)


def save_archive(archive: list[dict]):
    os.makedirs(DOCS_DIR, exist_ok=True)
    with open(ARCHIVE_JSON, "w", encoding="utf-8") as f:
        json.dump(archive, f, ensure_ascii=False, indent=2)


def update_archive(digest: list[dict], date_str: str) -> list[dict]:
    """Prepend today's digest to the archive, trim to MAX_DAYS_KEPT, save, return."""
    archive = load_archive()
    archive = [day for day in archive if day["date"] != date_str]  # avoid dup if rerun
    archive.insert(0, {"date": date_str, "stories": digest})
    archive = archive[:MAX_DAYS_KEPT]
    save_archive(archive)
    return archive


def render_day_html(day: dict, is_first: bool) -> str:
    stories = day["stories"]
    open_attr = " open" if is_first else ""

    if not stories:
        inner = '<p class="empty">No significant stories found.</p>'
    else:
        cards = ""
        for item in stories:
            color = CATEGORY_COLOR.get(item.get("category", ""), "#6b7280")
            cards += f"""
            <div class="card" style="border-left-color: {color};">
                <span class="badge" style="background: {color};">{item['category']}</span>
                <h3>{item['headline']}</h3>
                <p class="summary">{item['summary']}</p>
                <p class="relevance">🎯 {item['cat_relevance']}</p>
                <a class="source" href="{item['url']}" target="_blank" rel="noopener">{item['source']} →</a>
            </div>
            """
        inner = f'<div class="cards">{cards}</div>'

    return f"""
    <details class="day"{open_attr}>
        <summary>{day['date']}</summary>
        {inner}
    </details>
    """


def generate_page(archive: list[dict]):
    days_html = "".join(
        render_day_html(day, is_first=(i == 0)) for i, day in enumerate(archive)
    )

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>CAT Daily News Digest</title>
<style>
    :root {{
        color-scheme: light;
    }}
    body {{
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
        max-width: 760px;
        margin: 0 auto;
        padding: 24px 16px 80px;
        background: #fafafa;
        color: #111827;
        line-height: 1.5;
    }}
    h1 {{
        font-size: 26px;
        margin-bottom: 4px;
    }}
    .subtitle {{
        color: #6b7280;
        font-size: 14px;
        margin-bottom: 32px;
    }}
    .day {{
        margin-bottom: 16px;
    }}
    .day summary {{
        font-size: 18px;
        font-weight: 600;
        border-bottom: 2px solid #111827;
        padding-bottom: 8px;
        margin-bottom: 16px;
        cursor: pointer;
    }}
    .day[open] summary {{
        margin-bottom: 16px;
    }}
    .empty {{
        color: #9ca3af;
        font-style: italic;
    }}
    .card {{
        background: white;
        border-left: 4px solid #6b7280;
        border-radius: 6px;
        padding: 14px 16px;
        margin-bottom: 14px;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05);
    }}
    .badge {{
        display: inline-block;
        color: white;
        font-size: 11px;
        font-weight: 600;
        padding: 2px 8px;
        border-radius: 10px;
        margin-bottom: 8px;
    }}
    .card h3 {{
        margin: 6px 0 8px 0;
        font-size: 16px;
    }}
    .summary {{
        font-size: 14px;
        color: #374151;
        margin: 0 0 8px 0;
    }}
    .relevance {{
        font-size: 13px;
        color: #6b7280;
        font-style: italic;
        margin: 0 0 8px 0;
    }}
    .source {{
        font-size: 12px;
        color: #2563eb;
        text-decoration: none;
    }}
    .source:hover {{
        text-decoration: underline;
    }}
</style>
</head>
<body>
    <h1>📰 CAT Daily News Digest</h1>
    <p class="subtitle">Geopolitics · Economy · India National — generated daily for CAT prep</p>
    {days_html}
</body>
</html>
"""

    os.makedirs(DOCS_DIR, exist_ok=True)
    with open(os.path.join(DOCS_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(html)


if __name__ == "__main__":
    archive = load_archive()
    generate_page(archive)
    print(f"Generated page with {len(archive)} day(s) of archive")
