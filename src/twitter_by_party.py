"""
Get data from raw CSV data (Democracy Club) into the format for uploading
twitter usernames.
Output format e.g.
{
  "Labour": ["username1", "username2", ...],
  "Conservative": ["username3", ...],
  ...
}

"""

from pathlib import Path

from main import read_csv_data_from_file, write_out_json

CSV_FILENAME = "dc-candidates-election_date_2024-07-04__election_id_parl__field_group_results-person-candidacy__elected_true-2026-06-01T16-13-22"  # noqa


def get_twitter_usernames_by_party(df) -> dict[str, list[str]]:
    result = {}
    for party, group in df.groupby("party_name"):
        usernames = [u for u in group["twitter_username"] if u]
        result[party] = usernames
    return result


if __name__ == "__main__":
    df = read_csv_data_from_file(
        Path(__file__).parent / "raw_data" / f"{CSV_FILENAME}.csv"
    )
    twitter_by_party = get_twitter_usernames_by_party(df)
    write_out_json(data=twitter_by_party, filename=f"{CSV_FILENAME}-twitter-by-party")
