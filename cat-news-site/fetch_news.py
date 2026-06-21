"""
Fetches news from GNews API across three CAT-relevant categories,
deduplicates, and returns raw articles for summarization.
"""
import os
import requests
from datetime import datetime, timedelta, timezone

GNEWS_BASE_URL = "https://gnews.io/api/v4/search"

# Queries tuned for CAT GK/current-affairs relevance.
QUERIES = {
    "geopolitics": "international relations OR diplomacy OR war OR sanctions OR United Nations OR foreign policy",
    "economy": "RBI OR inflation OR GDP OR fiscal policy OR trade deficit OR stock market India OR global economy",
    "india_national": "India government policy OR Supreme Court India OR Parliament India OR Indian economy reform",
}

MAX_PER_CATEGORY = 6  # raw pull per category before LLM trims/prioritizes


def fetch_category(query: str, max_results: int = MAX_PER_CATEGORY):
    """Fetch recent articles for a given query from the last 26 hours."""
    since = (datetime.now(timezone.utc) - timedelta(hours=26)).strftime(
        "%Y-%m-%dT%H:%M:%SZ"
    )
    params = {
        "q": query,
        "lang": "en",
        "country": "in",
        "max": max_results,
        "from": since,
        "sortby": "publishedAt",
        "apikey": os.environ["GNEWS_API_KEY"],
    }
    resp = requests.get(GNEWS_BASE_URL, params=params, timeout=30)
    resp.raise_for_status()
    return resp.json().get("articles", [])


def fetch_all_news():
    """Fetch news across all categories, tagged by category, deduplicated by URL."""
    all_articles = []
    seen_urls = set()

    for category, query in QUERIES.items():
        try:
            articles = fetch_category(query)
        except requests.RequestException as e:
            print(f"Warning: failed to fetch '{category}': {e}")
            continue

        for art in articles:
            url = art.get("url")
            if not url or url in seen_urls:
                continue
            seen_urls.add(url)
            all_articles.append(
                {
                    "category": category,
                    "title": art.get("title", "").strip(),
                    "description": art.get("description", "").strip(),
                    "content": (art.get("content") or "").strip(),
                    "source": art.get("source", {}).get("name", "Unknown"),
                    "url": url,
                    "published_at": art.get("publishedAt", ""),
                }
            )

    return all_articles


if __name__ == "__main__":
    articles = fetch_all_news()
    print(f"Fetched {len(articles)} unique articles")
    for a in articles[:3]:
        print(f"- [{a['category']}] {a['title']} ({a['source']})")
