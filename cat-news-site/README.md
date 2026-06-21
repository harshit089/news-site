# CAT Daily News Website

A simple, free, self-updating website with a daily digest of geopolitics,
economy, and Indian national news — summarized for CAT prep relevance using
GPT-4o-mini.

## How it works

1. `fetch_news.py` pulls recent articles from GNews across three queries
   (geopolitics, economy, India national).
2. `summarize.py` sends them to GPT-4o-mini, which selects the 8-10 most
   CAT-relevant stories and writes plain-English summaries with exam
   relevance notes.
3. `generate_page.py` updates the website (docs/index.html) with today's
   digest, plus a 30-day collapsible archive.
4. `main.py` runs all of the above in sequence. GitHub Actions runs `main.py`
   every day at 7:00 AM IST and pushes the updated page automatically.

## One-time setup

### 1. Create the GitHub repository

- Go to github.com → "New repository"
- Name it e.g. `cat-news-site`, can be Public or Private
- Upload all files in this project (drag-and-drop on the GitHub web UI
  works, or use git from your machine)

### 2. Add your secrets

Repo → **Settings → Secrets and variables → Actions → New repository
secret**. Add:

| Secret name | Value |
|---|---|
| `GNEWS_API_KEY` | Your GNews API key (free at gnews.io) |
| `OPENAI_API_KEY` | Your OpenAI API key |

### 3. Enable GitHub Pages

Repo → **Settings → Pages** → "Build and deployment" → **Source: Deploy
from a branch**, **Branch: main**, **Folder: /docs** → Save.

Your site goes live at `https://<your-username>.github.io/cat-news-site/`
after the first run.

### 4. Test it manually

Repo → **Actions** tab → "Daily CAT News Digest" workflow → **"Run
workflow"** button → wait ~30-60 seconds → refresh your GitHub Pages URL.

If it fails, click into the run to see the error log — most common issues
are a typo'd secret name or an unfunded OpenAI API key (add a few dollars
of credit at platform.openai.com/settings/billing).

### 5. Done

Runs automatically every day at 7:00 AM IST from here on — bookmark the
page on your phone and check it each morning.

## Customizing

- **Change story count**: edit `MAX_PER_CATEGORY` in `fetch_news.py` and the
  selection guidance in `summarize.py`'s `SYSTEM_PROMPT`.
- **Change categories**: edit the `QUERIES` dict in `fetch_news.py`.
- **Change delivery time**: edit the `cron` line in
  `.github/workflows/daily-digest.yml` (UTC; IST = UTC+5:30).
- **Change archive length**: edit `MAX_DAYS_KEPT` in `generate_page.py`.

## Costs

- GNews: 100 requests/day free (this uses 3/day)
- GitHub Actions: free tier covers this easily (~1 min/day)
- GitHub Pages: free
- OpenAI gpt-4o-mini: roughly $0.001-0.003 per day's digest — a $1-2 top-up
  will likely last the better part of a year at this volume
