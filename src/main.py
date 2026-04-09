import json
from datetime import datetime
from pathlib import Path
import io

import pandas as pd
import httpx


DOWNLOAD_CSV_URL = "https://candidates.democracyclub.org.uk/data/export_csv/?election_date=2026-05-07&extra_fields=facebook_page_url&extra_fields=facebook_personal_url&extra_fields=linkedin_url&extra_fields=twitter_username&extra_fields=mastodon_username&extra_fields=youtube_profile&extra_fields=instagram_url&extra_fields=blue_sky_url&extra_fields=threads_url&extra_fields=tiktok_url&format=csv"

CSV_FIELD_TYPES = {
    "person_id": str,
    "person_name": str,
    "election_id": "category",
    "party_name": "category",
    "party_id": "category",
    "facebook_page_url": str,
    "facebook_personal_url": str,
    "linkedin_url": str,
    "twitter_username": str,
    "youtube_profile": str,
    "instagram_url": str,
    "blue_sky_url": str,
    "threads_url": str,
    "tiktok_url": str,
}

STR_COLS = [col for col, dtype in CSV_FIELD_TYPES.items() if dtype is str]


def get_list_of_candidate_data(df: pd.DataFrame) -> list[dict]:
    return df.to_dict("records")


def validate_election_data(df: pd.DataFrame) -> None:
    # TODO - do we care about duplicate people?
    # duplicates = df[df.duplicated(subset=["person_id", "election_id"], keep=False)]
    # if not duplicates.empty:
    #     duplicate_vals = duplicates[["person_id", "election_id"]].drop_duplicates().to_dict("records")
    #     raise ValueError(f"Duplicate (person_id, election_id) pairs found: {duplicate_vals}")
    inconsistent_party_data = (
        df.groupby("party_id")["party_name"]
        .nunique()
        .loc[lambda s: s > 1]
    )
    if not inconsistent_party_data.empty:
        raise ValueError(f"party_ids mapped to multiple party_names: {list(inconsistent_party_data.index)}")


def get_and_validate_df(data: Path | io.StringIO) -> pd.DataFrame:
    df = pd.read_csv(data, keep_default_na=False, dtype=CSV_FIELD_TYPES, usecols=CSV_FIELD_TYPES.keys())
    df[STR_COLS] = df[STR_COLS].apply(lambda col: col.str.strip('"'))
    print(f"CSV file has {len(df)} rows")
    validate_election_data(df)
    return df


def read_csv_data_from_file(filepath: Path) -> pd.DataFrame:
    print(f"Reading data from {filepath}")
    return get_and_validate_df(data=filepath)


def read_csv_data_from_url(url: str) -> pd.DataFrame:
    print(f"Reading data from {url}")
    response = httpx.get(url)
    response.raise_for_status()
    return get_and_validate_df(data=io.StringIO(response.text))


def get_candidate_data_by_column(df: pd.DataFrame, column_name: str) -> dict:
    unique_values = df[column_name].unique()
    output_dictionary = {}
    for val in unique_values:
        filtered_df = df[df[column_name] == val]
        output_dictionary[val] = get_list_of_candidate_data(filtered_df)
    return output_dictionary


def write_out_json(data: dict | list, filename_suffix: str) -> None:
    src_dir = Path(__file__).parent
    data_output_dir = src_dir / "data_outputs"
    timestamp = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
    output_path = data_output_dir / f"{timestamp}_{filename_suffix}.json"
    with open(output_path, "w+") as f:
        json.dump(data, f)
    print(f"Data written out to {output_path}")


if __name__ == "__main__":
    # TODO - change this to read from a file instead
    # csv_filepath = Path(__file__).parent / "raw_data" / "dc-candidates-scotland-2026-04-02T16-17-27.csv"
    # df = read_csv_data_from_file(csv_filepath)
    df = read_csv_data_from_url(DOWNLOAD_CSV_URL)
    candidates_by_election = get_candidate_data_by_column(df=df, column_name="election_id")
    write_out_json(data=candidates_by_election, filename_suffix="candidates_by_election")
    candidates_by_party_name = get_candidate_data_by_column(df=df, column_name="party_name")
    write_out_json(data=candidates_by_party_name, filename_suffix="candidates_by_party_name")
