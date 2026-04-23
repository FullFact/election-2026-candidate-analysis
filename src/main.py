import io
import json
from pathlib import Path

import httpx
import pandas as pd

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
        df.groupby("party_id")["party_name"].nunique().loc[lambda s: s > 1]
    )
    if not inconsistent_party_data.empty:
        raise ValueError(
            f"party_ids mapped to multiple party_names: {list(inconsistent_party_data.index)}"
        )


def get_and_validate_df(data: Path | io.StringIO) -> pd.DataFrame:
    df = pd.read_csv(
        data,
        keep_default_na=False,
        dtype=CSV_FIELD_TYPES,
        usecols=CSV_FIELD_TYPES.keys(),
    )  # type: ignore
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


def get_candidate_data_by_column(
    df: pd.DataFrame, column_name: str, values: list[str] | None = None
) -> dict:
    unique_values = df[column_name].unique()
    output_dictionary = {}
    for val in unique_values:
        col = val
        if values and col not in values:
            col = "other"

        filtered_df = df[df[column_name] == val]
        output_dictionary[col] = output_dictionary.get(
            col, []
        ) + get_list_of_candidate_data(filtered_df)
    return output_dictionary


def write_out_json(data: dict | list, filename: str) -> None:
    src_dir = Path(__file__).parent
    data_output_dir = src_dir / "data_outputs"
    output_path = data_output_dir / f"{filename}.json"
    with open(output_path, "w") as f:
        json.dump(data, f, indent="  ")
    print(f"Data written out to {output_path} ({len(data)} rows)")


if __name__ == "__main__":
    csv_filename = "mayor"
    df = read_csv_data_from_file(
        Path(__file__).parent / "raw_data" / f"{csv_filename}.csv"
    )
    # df = read_csv_data_from_url(DOWNLOAD_CSV_URL)
    # candidates_by_election = get_candidate_data_by_column(
    #     df=df, column_name="election_id"
    # )
    # write_out_json(
    #     data=candidates_by_election, filename_suffix="candidates_by_election"
    # )
    candidates_by_party_name = get_candidate_data_by_column(
        df=df,
        column_name="party_name",
        values=[
            "Labour Party",
            "Labour and Co-operative Party",
            "Conservative and Unionist Party",
            "Liberal Democrats",
            "Reform UK",
            "Scottish National Party (SNP)",
            "Scottish Green Party",
            "Green Party",
            "Plaid Cymru - The Party of Wales",
        ],
    )

    write_out_json(
        data=candidates_by_party_name,
        filename=f"{csv_filename}-candidates-by-party",
    )
