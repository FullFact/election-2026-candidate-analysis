import argparse
import json
import sys
import time
from pathlib import Path

import httpx

API_URL = "https://ai.fullfact.org/api/publications_v2/"

# Throwaway bearer token. JWTs from ai.fullfact.org expire in ~10 minutes,
# so paste a fresh one from the browser before running.
BEARER_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0eXBlIjoiYWNjZXNzIiwidXNlcl9pZCI6NDQ1LCJvcmdhbmlzYXRpb25faWQiOjk0LCJyb2xlIjoiYWRtaW5pc3RyYXRvciIsImlzcyI6ImZ1bGxmYWN0Iiwic3ViIjoiYWxwaGEiLCJleHAiOjE3NzYyNjE4MDguMDk3MDQ3NiwiaWF0IjoxNzc2MjYxMjA4LjA5NzA0NzZ9.eqU5CKlyK0F2KU-zODh7pziAXGNE1GEzscHHQ9UlwRY"

# Keys are the filename prefix before the first '-'; values are the region word
# prepended to each party name (unless the party already starts with it).
REGION_PREFIXES = {
    "scottish": "Scottish",
    "welsh": "Welsh",
    "local": "English Local",
}


def region_prefix_for_file(filename: str) -> str:
    stem = Path(filename).name
    for key, prefix in REGION_PREFIXES.items():
        if stem.startswith(f"{key}-"):
            return prefix
    return ""


def build_publication_name(person_name: str, party_name: str, region: str) -> str:
    party_name = party_name.strip()
    if region and not party_name.lower().startswith(region.lower()):
        party_name = f"{region} {party_name}"
    return f"{person_name.strip()} - {party_name}"


def candidates_with_youtube(data: dict) -> list[dict]:
    # The "other" bucket uses the same candidate shape as named parties, so we
    # can iterate every value uniformly — each candidate already carries its
    # real party_name.
    results = []
    for candidates in data.values():
        for candidate in candidates:
            if candidate.get("youtube_profile", "").strip():
                results.append(candidate)
    return results


def post_publication(
    client: httpx.Client, publication_name: str, media_url: str
) -> httpx.Response:
    return client.post(
        API_URL,
        json={
            "publication_name": publication_name,
            "wikidata_publication_id": "",
            "media_url": media_url,
        },
        headers={
            # The API uses the British spelling "authorisation".
            "authorisation": f"Bearer {BEARER_TOKEN}",
            "content-type": "application/json",
        },
    )


def main():
    parser = argparse.ArgumentParser(
        description="POST candidate YouTube accounts to the Full Fact live API"
    )
    parser.add_argument(
        "json_file",
        type=Path,
        help="Path to a *-candidates-by-party.json file",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would be sent without making HTTP requests",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=0.5,
        help="Seconds to sleep between requests (default: 0.5)",
    )
    args = parser.parse_args()

    region = region_prefix_for_file(args.json_file.name)
    with open(args.json_file) as f:
        data = json.load(f)

    candidates = candidates_with_youtube(data)
    print(
        f"Found {len(candidates)} candidates with a youtube_profile in {args.json_file.name}"
    )

    if args.dry_run:
        for c in candidates:
            name = build_publication_name(c["person_name"], c["party_name"], region)
            print(f"DRY RUN: {name} -> {c['youtube_profile']}")
        return

    ok = 0
    failed = 0
    with httpx.Client(timeout=30.0) as client:
        for c in candidates:
            publication_name = build_publication_name(
                c["person_name"], c["party_name"], region
            )
            media_url = c["youtube_profile"].strip()
            try:
                resp = post_publication(client, publication_name, media_url)
                if resp.is_success:
                    ok += 1
                    print(f"OK:  {publication_name} -> {media_url}")
                else:
                    failed += 1
                    print(
                        f"ERR {resp.status_code}: {publication_name} -> {media_url}: {resp.text[:200]}",
                        file=sys.stderr,
                    )
            except Exception as e:
                failed += 1
                print(
                    f"FAIL: {publication_name} -> {media_url}: {e}",
                    file=sys.stderr,
                )
            time.sleep(args.delay)

    print(f"\nDone. ok={ok} failed={failed} total={len(candidates)}")


if __name__ == "__main__":
    main()
