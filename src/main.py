import json
from pathlib import Path

import pandas as pd


def get_list_of_candidate_data(df: pd.DataFrame) -> list[dict]:
    allcandidates = []
    for _, row in df.iterrows():
        dictionary = {
            "person_name": row["person_name"],
            "person_id": row["person_id"],
            "party_name": row["party_name"],
        }
        allcandidates.append(dictionary)
    return allcandidates


def get_candidate_data_by_election_id(df: pd.DataFrame) -> dict:
    election_ids = df["election_id"].unique()
    output_dictionary = {}
    for i in election_ids:
        filtered_df = df[df["election_id"] == i]
        output_dictionary[i] = get_list_of_candidate_data(filtered_df)
    return output_dictionary


if __name__ == "__main__":
    src_dir = Path(__file__).parent
    df = pd.read_csv(src_dir / "raw_data/dc-candidates-scotland-2026-04-02T16-17-27.csv")

    result = get_candidate_data_by_election_id(df)
    print(json.dumps(result, indent=4))

    with open(src_dir / "data_outputs/candidates.json", "w+") as f:
        json.dump(result, f)
