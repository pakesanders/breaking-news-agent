import requests
import xml.etree.ElementTree as ET
import json
import os
from urllib.parse import urlparse
from email.utils import parsedate_to_datetime
from datetime import datetime, timezone, timedelta

from ai_classifier import classify_post
from telegram import send_telegram_message


MONITORED_ACCOUNTS = {
    "NFL": [
        "AdamSchefter",
        "RapSheet",
        "NFL"
    ],
    "NBA": [
        "ShamsCharania",
        "wojespn"
    ],
    "MLB": [
        "JeffPassan",
        "MLB"
    ],
    "NHL": [
        "TSNBobMcKenzie"
    ]
}


SEEN_FILE = "seen_posts.json"

# Only consider posts from the last 5 minutes
RECENT_MINUTES = 5


def load_seen_posts():
    if not os.path.exists(SEEN_FILE):
        return set()

    try:
        with open(SEEN_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)

        return set(data.get("posts", []))

    except Exception:
        return set()


def save_seen_posts(seen_posts):
    with open(SEEN_FILE, "w", encoding="utf-8") as file:
        json.dump(
            {
                "posts": sorted(list(seen_posts))
            },
            file,
            indent=2
        )


def get_posts(account):
    feed_url = f"https://fxtwitter.com/{account}/feed.xml"

    response = requests.get(
        feed_url,
        timeout=15,
        headers={
            "User-Agent": "SportsNewsAI/1.0"
        }
    )

    response.raise_for_status()

    root = ET.fromstring(response.text)

    posts = []

    for item in root.findall(".//item"):

        title = item.findtext("title", default="")
        link = item.findtext("link", default="")
        pub_date = item.findtext("pubDate", default="")

        try:
            path_parts = urlparse(link).path.strip("/").split("/")

            if len(path_parts) < 3:
                continue

            actual_account = path_parts[0].lower()
            post_id = path_parts[2]

            if actual_account != account.lower():
                continue

            if not post_id.isdigit():
                continue

        except Exception:
            continue

        posts.append({
            "account": account,
            "text": title,
            "url": link,
            "published": pub_date,
            "id": post_id
        })

    return posts


def is_recent(pub_date):
    try:
        post_time = parsedate_to_datetime(pub_date)

        if post_time.tzinfo is None:
            post_time = post_time.replace(tzinfo=timezone.utc)

        now = datetime.now(timezone.utc)

        age = now - post_time

        return (
            age <= timedelta(minutes=RECENT_MINUTES)
            and age >= timedelta(minutes=-5)
        )

    except Exception:
        return False


def main():

    print("Sports News Monitor")
    send_telegram_message("🏆 Sports News AI test — Telegram connection is working!")
    print("=" * 50)

    seen_posts = load_seen_posts()

    new_posts = []

    total_posts = 0
    recent_posts = 0

    for sport, accounts in MONITORED_ACCOUNTS.items():

        print(f"\n{sport}")
        print("-" * 30)

        for account in accounts:

            print(f"\nChecking @{account}...")

            try:

                posts = get_posts(account)

                print(f"Found {len(posts)} verified posts.")

                total_posts += len(posts)

                for post in posts:

                    post_id = f"{account.lower()}:{post['id']}"

                    if not is_recent(post["published"]):
                        continue

                    recent_posts += 1

                    if post_id not in seen_posts:

                        new_posts.append(post)

                        try:

                            ai_result = classify_post(post)

                            post["ai"] = ai_result

                        except Exception as e:

                            print(
                                f"AI ERROR for @{post['account']}: {e}"
                            )

            except Exception as e:

                print(f"ERROR checking @{account}: {e}")

    print("\n" + "=" * 50)

    print(f"TOTAL POSTS FOUND: {total_posts}")
    print(f"RECENT POSTS: {recent_posts}")
    print(f"NEW RECENT POSTS: {len(new_posts)}")

    for post in new_posts:

        print("\n--- NEW POST ---")

        print(f"Account: @{post['account']}")
        print(f"Date: {post['published']}")
        print(f"Post: {post['text']}")
        print(f"URL: {post['url']}")

        if "ai" in post:

            classification = post["ai"].get("classification")

            print("\n--- GEMINI CLASSIFICATION ---")

            print(f"Classification: {classification}")
            print(f"Sport: {post['ai'].get('sport')}")
            print(f"Category: {post['ai'].get('category')}")
            print(f"Summary: {post['ai'].get('summary')}")
            print(f"Reason: {post['ai'].get('reason')}")

            if classification == "IMPORTANT":

                print("\n🚨 SENDING TELEGRAM")

                message = (
                    f"🚨 BREAKING SPORTS NEWS\n\n"
                    f"@{post['account']}\n"
                    f"{post['ai'].get('summary')}\n\n"
                    f"{post['url']}"
                )

                send_telegram_message(message)

            elif classification == "PROBABLY IMPORTANT":

                print("\n🔔 SENDING TELEGRAM")

                message = (
                    f"🔔 SPORTS NEWS\n\n"
                    f"@{post['account']}\n"
                    f"{post['ai'].get('summary')}\n\n"
                    f"{post['url']}"
                )

                send_telegram_message(message)

            else:

                print("\n⏭️ WOULD IGNORE")

    for sport, accounts in MONITORED_ACCOUNTS.items():

        for account in accounts:

            try:

                posts = get_posts(account)

                for post in posts:

                    post_id = f"{account.lower()}:{post['id']}"

                    seen_posts.add(post_id)

            except Exception:
                pass

    save_seen_posts(seen_posts)

    print("\n" + "=" * 50)

    print(f"REMEMBERING {len(seen_posts)} POSTS")

    print("Monitoring complete.")


if __name__ == "__main__":
    main()
