import requests
import xml.etree.ElementTree as ET


ACCOUNT = "TSNBobMcKenzie"
FEED_URL = f"https://fxtwitter.com/{ACCOUNT}/feed.xml"


def get_latest_posts():
    response = requests.get(
        FEED_URL,
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

        posts.append({
            "account": ACCOUNT,
            "text": title,
            "url": link,
            "published": pub_date
        })

    return posts


def main():
    print(f"Checking @{ACCOUNT}...")

    posts = get_latest_posts()

    if not posts:
        print("No posts found.")
        return

    print(f"Found {len(posts)} posts.")

    for post in posts[:5]:
        print("\n---")
        print(f"Account: @{post['account']}")
        print(f"Date: {post['published']}")
        print(f"Post: {post['text']}")
        print(f"URL: {post['url']}")


if __name__ == "__main__":
    main()
