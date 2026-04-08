import json
from datetime import datetime
from pathlib import Path

import pandas as pd


def get_list_of_candidate_data(df: pd.DataFrame) -> list[dict]:
    candidates_data_list = []
    for _, row in df.iterrows():
        candidate_dictionary = {}
        # TODO - remove some of these
        fields_to_include = [
            'person_id', 'person_name', 'election_id', 'ballot_paper_id',
            'election_date', 'election_current', 'party_name', 'party_id',
            'post_label', 'cancelled_poll', 'seats_contested', 'facebook_page_url',
            'linkedin_url', 'twitter_username', 'youtube_profile', 'instagram_url',
            'blue_sky_url', 'threads_url', 'tiktok_url'
        ]
        for fieldname in fields_to_include:
            candidate_dictionary[fieldname] = row[fieldname]
        candidates_data_list.append(candidate_dictionary)
    return candidates_data_list


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


if __name__ == "__main__":
    src_dir = Path(__file__).parent
    df = pd.read_csv(src_dir / "raw_data/dc-candidates-scotland-2026-04-02T16-17-27.csv")
    candidates_by_election = get_candidate_data_by_column(df=df, column_name="election_id")
    write_out_json(data=candidates_by_election, filename_suffix="candidates_by_election")
