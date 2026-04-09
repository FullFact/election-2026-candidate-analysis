import json
from datetime import datetime
from pathlib import Path
import io

import pandas as pd
import httpx

# https://candidates.democracyclub.org.uk/data/download_reason/?election_id=sp.c%7Cr.2026-05-07&format=csv


download_csv_url = "https://candidates.democracyclub.org.uk/data/download_reason/?election_date=2026-05-07&format=csv"

def get_list_of_candidate_data(df: pd.DataFrame) -> list[dict]:
    candidates_data_list = []
    for _, row in df.iterrows():
        candidate_dictionary = {}
        fields_to_include = [
            'person_id', 'person_name', 'election_id', 'party_name', 'party_id',
            'facebook_page_url', 'linkedin_url', 'twitter_username', 'youtube_profile', 'instagram_url',
            'blue_sky_url', 'threads_url', 'tiktok_url'
        ]
        for fieldname in fields_to_include:
            candidate_dictionary[fieldname] = row[fieldname]
        candidates_data_list.append(candidate_dictionary)
    return candidates_data_list



def validate_election_data(df: pd.DataFrame) -> None:
    duplicates = df[df.duplicated(subset=["person_id", "election_id"], keep=False)]
    if not duplicates.empty:
        duplicate_vals = duplicates[["person_id", "election_id"]].drop_duplicates().to_dict("records")
        raise ValueError(f"Duplicate (person_id, election_id) pairs found: {duplicate_vals}")
    inconsistent_party_data = (
        df.groupby("party_id")["party_name"]
        .nunique()
        .loc[lambda s: s > 1]
    )
    if not inconsistent_party_data.empty:
        raise ValueError(f"party_ids mapped to multiple party_names: {list(inconsistent_party_data.index)}")



def read_csv_data_from_file(filepath: Path) -> pd.DataFrame:
    print(f"Reading data from {filepath}")
    df = pd.read_csv(filepath)
    print(f"CSV file has {len(df)} rows")
    validate_election_data(df)
    return df


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
    csv_filepath = Path(__file__).parent / "raw_data" / "dc-candidates-scotland-2026-04-02T16-17-27.csv"
    df = read_csv_data_from_file(csv_filepath)
    candidates_by_election = get_candidate_data_by_column(df=df, column_name="election_id")
    write_out_json(data=candidates_by_election, filename_suffix="candidates_by_election")
    candidates_by_party_name = get_candidate_data_by_column(df=df, column_name="party_name")
    write_out_json(data=candidates_by_party_name, filename_suffix="candidates_by_party_name")

    # response = httpx.get(download_csv_url)
    # print(response)
    # print(response.content)

