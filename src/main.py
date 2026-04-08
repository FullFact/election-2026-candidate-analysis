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


def get_candidate_data_by_election_id(df: pd.DataFrame) -> dict:
    election_ids = df["election_id"].unique()
    output_dictionary = {}
    for i in election_ids:
        filtered_df = df[df["election_id"] == i]
        output_dictionary[i] = get_list_of_candidate_data(filtered_df)
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
    result = get_candidate_data_by_election_id(df)
    write_out_json(data=result, filename_suffix="candidates_by_election")
