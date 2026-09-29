# Sports News Monitor

# X/Twitter accounts we want to monitor
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


def main():
    print("Sports News Monitor started.")
    print("=" * 40)

    for sport, accounts in MONITORED_ACCOUNTS.items():
        print(f"\n{sport}:")

        for account in accounts:
            print(f"  - @{account}")

    print("\nMonitoring complete.")


if __name__ == "__main__":
    main()
