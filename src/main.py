import json
from pathlib import Path

import pandas as pd


def getlistofcandidates(df):
    allcandidates = []
    for index, row in df.iterrows():
        dictionary = {
            "person_name": row["person_name"],
            "person_id": row["person_id"],
            "party_name": row["party_name"],
        }
        allcandidates.append(dictionary)
    return allcandidates


def getfullelectionjson(df):
    electionids = df["election_id"].unique()
    dictionary = {}
    for i in electionids:
        filtereddf = df[df["election_id"] == i]
        dictionary[i] = getlistofcandidates(filtereddf)
    return dictionary


if __name__ == "__main__":
    src_dir = Path(__file__).parent
    df = pd.read_csv(src_dir / "raw_data/dc-candidates-scotland-2026-04-02T16-17-27.csv")

    result = getfullelectionjson(df)
    print(json.dumps(result, indent=4))

    with open(src_dir / "data_outputs/candidates.json", "w+") as f:
        json.dump(result, f)
