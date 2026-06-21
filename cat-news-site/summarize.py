"""
Takes raw fetched articles and uses GPT-4o-mini to produce a CAT-aspirant
focused digest: prioritized, concise, exam-relevant.
"""
import os
import json
from openai import OpenAI

MODEL = "gpt-4o-mini"

SYSTEM_PROMPT = """You are a current-affairs editor for a CAT (Common Admission Test) MBA \
aspirant in India. Your job is to turn a raw batch of news articles into a tight, \
high-signal daily digest.

Selection criteria (be ruthless):
- Prioritize stories with genuine relevance to CAT GK/current-affairs sections, \
  Static GK linkages, or broader analytical/case-study value (geopolitics, \
  Indian economy & policy, India's institutions, global trade/finance, major \
  international relations developments).
- Skip celebrity news, sports (unless a major India policy angle), routine \
  crime stories, or anything with no lasting relevance.
- Merge duplicate/near-duplicate stories covering the same event into one entry.
- Select the most important 8-10 stories from the batch given to you. Quality \
  over quantity — if fewer truly matter, return fewer.

For each selected story produce:
- "headline": short, punchy, plain-English headline (not clickbait)
- "category": one of "Geopolitics", "Economy", "India National"
- "summary": 3-4 sentences. Explain WHAT happened, WHY it matters, and any \
  background context a newspaper would assume you already know. Write for \
  someone with no prior context on this specific story, but who is generally \
  well-read. No jargon without a one-clause explanation.
- "cat_relevance": one short sentence on why/how this could matter for CAT \
  prep (e.g. "Useful for GK on India-China relations" or "Illustrates RBI's \
  inflation-targeting framework").
- "source": the source name passed to you
- "url": the article URL passed to you

Respond with ONLY a JSON object of the form {"stories": [...]}, nothing else. \
No markdown fences, no preamble, no commentary."""


def summarize_articles(articles: list[dict]) -> list[dict]:
    """Send raw articles to GPT-4o-mini and get back a structured, prioritized digest."""
    if not articles:
        return []

    compact = [
        {
            "title": a["title"],
            "description": a["description"],
            "content_snippet": a["content"][:500],
            "source": a["source"],
            "url": a["url"],
            "category_hint": a["category"],
        }
        for a in articles
    ]

    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

    response = client.chat.completions.create(
        model=MODEL,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": (
                    "Here is today's batch of raw articles as JSON. Select and "
                    "summarize per your instructions:\n\n"
                    + json.dumps(compact, ensure_ascii=False)
                ),
            },
        ],
    )

    raw_text = response.choices[0].message.content.strip()

    try:
        parsed = json.loads(raw_text)
    except json.JSONDecodeError as e:
        print("Failed to parse model output as JSON:", e)
        print("Raw output was:", raw_text[:1000])
        raise

    # Model returns {"stories": [...]} per the json_object response format requirement
    digest = parsed.get("stories", []) if isinstance(parsed, dict) else parsed
    return digest


if __name__ == "__main__":
    dummy = [
        {
            "category": "economy",
            "title": "RBI holds repo rate steady at 6.5%",
            "description": "The Reserve Bank of India kept rates unchanged for the sixth straight meeting.",
            "content": "The Monetary Policy Committee voted 5-1 to hold rates...",
            "source": "Test Source",
            "url": "https://example.com/test",
            "published_at": "2026-06-21T08:00:00Z",
        }
    ]
    result = summarize_articles(dummy)
    print(json.dumps(result, indent=2))
