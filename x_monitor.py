import requests
import xml.etree.ElementTree as ET
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

        # Make sure the X URL actually belongs to the account
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

    total_posts = 0

    for sport, accounts in MONITORED_ACCOUNTS.items():
        print(f"\n{sport}")
        print("-" * 30)

        for account in accounts:
            print(f"\nChecking @{account}...")

            try:
                posts = get_posts(account)

                print(f"Found {len(posts)} verified posts.")

                for post in posts[:3]:
                    print("\n  ---")
                    print(f"  Account: @{post['account']}")
                    print(f"  Date: {post['published']}")
                    print(f"  Post: {post['text']}")
                    print(f"  URL: {post['url']}")

                total_posts += len(posts)

            except Exception as e:
                print(f"ERROR checking @{account}: {e}")

    print("\n" + "=" * 50)
    print(f"Total verified posts found: {total_posts}")
    print("Monitoring complete.")


if __name__ == "__main__":
    main()
