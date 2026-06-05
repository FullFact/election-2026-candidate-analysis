"""
Takes data from JSON an uploads to twitter list.
"""

import argparse
import asyncio
import json
import random
import sys

from twscrape import API

GQL_BASE = "https://x.com/i/api/graphql"

LIST_ADD_MEMBER_QUERY_ID = "vWPi0CTMoPFsjsL6W4IynQ"
LIST_ADD_MEMBER_URL = f"{GQL_BASE}/{LIST_ADD_MEMBER_QUERY_ID}/ListAddMember"

LIST_MEMBER_QUERY_ID = "oIetCo19avgStX4mOnGsPg"
LIST_MEMBER_URL = f"{GQL_BASE}/{LIST_MEMBER_QUERY_ID}/ListMembers"

CREATE_LIST_QUERY_ID = "UQRa0jJ9doxGEIQRea1Y0w"
CREATE_LIST_URL = f"{GQL_BASE}/{CREATE_LIST_QUERY_ID}/CreateList"


GQL_FEATURES = {
    "rweb_tipjar_consumption_enabled": True,
    "responsive_web_graphql_exclude_directive_enabled": True,
    "verified_phone_label_enabled": False,
    "responsive_web_graphql_skip_user_profile_image_extensions_enabled": False,
    "responsive_web_graphql_timeline_navigation_enabled": True,
}


async def make_gql_request(api: API, url: str, query_id: str, variables: dict) -> dict:
    acc = await api.pool.get_for_queue("ListAddMember")
    if not acc:
        raise RuntimeError("No available account in the pool")

    client = acc.make_client()
    try:
        payload = {
            "variables": variables,
            "features": GQL_FEATURES,
            "queryId": query_id,
        }
        resp = await client.post(url, json=payload)
        resp.raise_for_status()
        return resp.json()
    finally:
        await client.aclose()
        await api.pool.unlock(acc.username, "ListAddMember")


async def resolve_user_id(api: API, username: str) -> int:
    user = await api.user_by_login(username)
    if user is None:
        raise ValueError(f"User not found: @{username}")
    return user.id


async def create_list(
    api: API, name: str, description: str = "", private: bool = False
) -> str:
    if name == "S - Scottish National Pa":
        return "2044091169697825242"
    if name == "W - Conservative and Uni":
        return "2044501474571432297"
    if name == "S - other":
        return "2044479191928754431"

    variables = {
        "isPrivate": private,
        "name": name,
        "description": description,
    }
    result = await make_gql_request(
        api, CREATE_LIST_URL, CREATE_LIST_QUERY_ID, variables
    )
    list_data = result.get("data", {}).get("list", {})
    list_id = list_data.get("id_str") or list_data.get("id")
    if not list_id:
        raise RuntimeError(f"Failed to create list '{name}': {result}")
    return str(list_id)


async def add_to_list(api: API, list_id: str, user_id: int) -> dict:
    variables = {
        "listId": list_id,
        "userId": str(user_id),
    }
    return await make_gql_request(
        api, LIST_ADD_MEMBER_URL, LIST_ADD_MEMBER_QUERY_ID, variables
    )


def _parse_members_page(result: dict) -> tuple[list[str], str | None]:
    instructions = result["data"]["list"]["members_timeline"]["timeline"][
        "instructions"
    ]
    entries = next(
        i["entries"] for i in instructions if i["type"] == "TimelineAddEntries"
    )
    screen_names = [
        e["content"]["itemContent"]["user_results"]["result"]["core"]["screen_name"]
        for e in entries
        if e["content"].get("entryType") == "TimelineTimelineItem"
    ]
    cursor = next(
        (
            e["content"]["value"]
            for e in entries
            if e["content"].get("cursorType") == "Bottom"
        ),
        None,
    )
    return screen_names, cursor


async def list_members(api: API, list_id: str) -> list[str]:
    all_screen_names = []
    cursor = None
    while True:
        variables = {"listId": list_id}
        if cursor:
            variables["cursor"] = cursor
        result = await make_gql_request(
            api, LIST_MEMBER_URL, LIST_MEMBER_QUERY_ID, variables
        )
        screen_names, cursor = _parse_members_page(result)
        all_screen_names.extend(screen_names)
        print(f"Fetched {len(screen_names)} members (total: {len(all_screen_names)})")
        if not cursor or not screen_names:
            break
        await asyncio.sleep(random.uniform(2, 4))
    return all_screen_names


async def add_username_to_list(api: API, list_id: str, username: str) -> bool:
    """Resolve and add a username to a list. Returns False if rate limited."""
    user_id = await resolve_user_id(api, username)
    print(f"Got id {user_id} for {username}")
    result = await add_to_list(api, list_id, user_id)
    if "errors" in result:
        print(f"  Error adding @{username}: {result['errors']}", file=sys.stderr)
        codes = [r["code"] for r in result["errors"]]
        if 104 in codes:
            print("Rate limit reached")
            return False
        print(f"  Added @{username} (id={user_id})")  # Sometimes errors but still adds
    else:
        print(f"  Added @{username} (id={user_id})")
    await asyncio.sleep(random.uniform(4, 10))
    return True


async def main() -> None:
    parser = argparse.ArgumentParser(description="Add Twitter users to a list")
    parser.add_argument(
        "--db",
        default="accounts.db",
        help="twscrape accounts database (default: accounts.db)",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    manual_parser = subparsers.add_parser(
        "manual", help="Add usernames to an existing list"
    )
    manual_parser.add_argument("--list-id", required=True, help="Twitter list ID")
    manual_parser.add_argument(
        "usernames", nargs="+", help="Twitter usernames to add (without @)"
    )

    get_members_parser = subparsers.add_parser(
        "get-members", help="Print all usernames in a list"
    )
    get_members_parser.add_argument("--list-id", required=True, help="Twitter list ID")

    from_json_parser = subparsers.add_parser(
        "from-json", help="Create lists from a party JSON file"
    )
    from_json_parser.add_argument(
        "json_file", help="Path to JSON file mapping party names to usernames"
    )
    from_json_parser.add_argument(
        "--prefix",
        default="",
        help="Prefix for list names (e.g. 'Local 2026 - ')",
    )
    from_json_parser.add_argument(
        "--private",
        action="store_true",
        help="Create private lists",
    )

    args = parser.parse_args()
    api = API(args.db)

    if args.command == "get-members":
        screen_names = await list_members(api, args.list_id)
        print(",".join(screen_names))

    elif args.command == "manual":
        usernames = [u.lstrip("@") for u in args.usernames]
        for username in usernames:
            try:
                if not await add_username_to_list(api, args.list_id, username):
                    return
            except Exception as e:
                print(f"Failed to add @{username}: {e}", file=sys.stderr)

    elif args.command == "from-json":
        with open(args.json_file) as f:
            parties = json.load(f)

        for party, usernames in parties.items():
            list_name = f"{args.prefix}{party}"
            list_name = list_name[:24]
            print(f"\nCreating list: {list_name} ({len(usernames)} accounts)")

            try:
                list_id = await create_list(api, list_name, private=args.private)
                print(f"  Created list id={list_id}")
            except Exception as e:
                print(f"  Failed to create list '{list_name}': {e}", file=sys.stderr)
                continue

            for username in usernames:
                username = username.lstrip("@")
                try:
                    if not await add_username_to_list(api, list_id, username):
                        return
                except Exception as e:
                    print(f"  Failed to add @{username}: {e}", file=sys.stderr)


if __name__ == "__main__":
    asyncio.run(main())
