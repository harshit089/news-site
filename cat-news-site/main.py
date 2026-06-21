"""
Main entry point: fetches news, summarizes it with GPT-4o-mini, and updates
the GitHub Pages website. Run daily via GitHub Actions.
"""
import sys
from datetime import datetime, timezone, timedelta

from fetch_news import fetch_all_news
from summarize import summarize_articles
from generate_page import update_archive, generate_page

# IST = UTC+5:30, used for the human-readable date on the page
IST = timezone(timedelta(hours=5, minutes=30))


def main():
    date_str = datetime.now(IST).strftime("%A, %d %B %Y")

    print(f"[{date_str}] Fetching news...")
    articles = fetch_all_news()
    print(f"Fetched {len(articles)} unique raw articles")

    if not articles:
        print("No articles fetched today")
        digest = []
    else:
        print("Summarizing with GPT-4o-mini...")
        digest = summarize_articles(articles)
        print(f"Digest contains {len(digest)} stories")

    print("Updating webpage archive...")
    archive = update_archive(digest, date_str)
    generate_page(archive)

    print("\nDone. Webpage updated.")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)
