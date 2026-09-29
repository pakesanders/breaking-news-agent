import requests
import xml.etree.ElementTree as ET
import json
import os
from urllib.parse import urlparse


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
                "posts": list(seen_posts)
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

            if len(path_parts) < 2:
                continue

            actual_account = path_parts[0].lower()

            if actual_account != account.lower():
                continue

        except Exception:
            continue

        posts.append({
            "account": account,
            "text": title,
            "url": link,
            "published": pub_date
        })

    return posts


def main():
    print("Sports News Monitor")
    print("=" * 50)

    seen_posts = load_seen_posts()
    new_posts = []

    for sport, accounts in MONITORED_ACCOUNTS.items():
        print(f"\n{sport}")
        print("-" * 30)

        for account in accounts:
            print(f"\nChecking @{account}...")

            try:
                posts = get_posts(account)

                print(f"Found {len(posts)} verified posts.")

                for post in posts:
                    post_id = post["url"]

                    if post_id not in seen_posts:
                        new_posts.append(post)

            except Exception as e:
                print(f"ERROR checking @{account}: {e}")

    print("\n" + "=" * 50)
    print(f"NEW POSTS FOUND: {len(new_posts)}")

    for post in new_posts:
        print("\n--- NEW POST ---")
        print(f"Account: @{post['account']}")
        print(f"Date: {post['published']}")
        print(f"Post: {post['text']}")
        print(f"URL: {post['url']}")

    # Remember every post we have now seen
    for sport, accounts in MONITORED_ACCOUNTS.items():
        for account in accounts:
            try:
                posts = get_posts(account)

                for post in posts:
                    seen_posts.add(post["url"])

            except Exception:
                pass

    save_seen_posts(seen_posts)

    print("\n" + "=" * 50)
    print(f"Remembering {len(seen_posts)} posts.")
    print("Monitoring complete.")


if __name__ == "__main__":
    main()
