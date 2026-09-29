import os
import json
import requests


GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]

GEMINI_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    "gemini-3.5-flash-lite:generateContent"
)


def classify_post(post):
    prompt = f"""
You are the AI breaking-news classifier for a sports news alert system.

Analyze the following social media post.

Your job is to determine whether the post contains meaningful sports news.

Classify it as exactly one of:

IMPORTANT
PROBABLY IMPORTANT
UNIMPORTANT

IMPORTANT:
Major breaking sports news that fans would reasonably want to know immediately.
Examples include major trades, major signings, significant injuries, suspensions,
major transactions, major coaching changes, or other events with substantial
immediate impact.

PROBABLY IMPORTANT:
Potentially meaningful sports news that may matter to fans but is less clearly
urgent or significant.

UNIMPORTANT:
Routine posts, opinions, advertisements, promotions, jokes, game commentary,
ordinary statistics, generic announcements, or content with little immediate
news value.

Also identify the sport and category.

Return ONLY valid JSON in exactly this structure:

{{
  "classification": "IMPORTANT",
  "sport": "NFL",
  "category": "trade",
  "summary": "One short sentence explaining what happened.",
  "reason": "One short sentence explaining why this classification was chosen."
}}

Post account:
@{post["account"]}

Post text:
{post["text"]}

Post URL:
{post["url"]}
"""

    headers = {
        "Content-Type": "application/json"
    }

    params = {
        "key": GEMINI_API_KEY
    }

    data = {
        "contents": [
            {
                "parts": [
                    {
                        "text": prompt
                    }
                ]
            }
        ]
    }

    response = requests.post(
        GEMINI_URL,
        headers=headers,
        params=params,
        json=data,
        timeout=30
    )

    response.raise_for_status()

    result = response.json()

    text = result["candidates"][0]["content"]["parts"][0]["text"]

    text = text.strip()

    if text.startswith("```"):
        text = text.replace("```json", "")
        text = text.replace("```", "")
        text = text.strip()

    return json.loads(text)
