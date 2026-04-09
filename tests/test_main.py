import io

import pandas as pd
import pytest

from main import (  # type: ignore
    get_candidate_data_by_column,
    get_list_of_candidate_data,
    validate_election_data,
    get_and_validate_df,
    CSV_FIELD_TYPES
)

ALL_FIELDS = list(CSV_FIELD_TYPES.keys())


def make_candidate(**overrides) -> dict:
    defaults = {
        "person_id": "1", "person_name": "Alice Smith",
        "election_id": "local.2026", "party_name": "Party A", "party_id": "PP1",
        "facebook_page_url": "", "facebook_personal_url": "", "linkedin_url": "",
        "twitter_username": "", "youtube_profile": "", "instagram_url": "",
        "blue_sky_url": "", "threads_url": "", "tiktok_url": "",
    }
    return {**defaults, **overrides}


@pytest.fixture
def sample_df():
    return pd.DataFrame([
        make_candidate(person_id="1", person_name="Alice Smith", election_id="local.2026", party_name="Party A", party_id="PP1"),
        make_candidate(person_id="2", person_name="Bob Jones", election_id="local.2026", party_name="Party B", party_id="PP2"),
        make_candidate(person_id="3", person_name="Carol White", election_id="regional.2026", party_name="Party A", party_id="PP1"),
    ])


class TestGetListOfCandidateData:
    def test_length_matches_dataframe(self, sample_df):
        result = get_list_of_candidate_data(sample_df)
        assert len(result) == len(sample_df)

    def test_each_entry_has_all_fields(self, sample_df):
        result = get_list_of_candidate_data(sample_df)
        for candidate in result:
            assert set(candidate.keys()) == set(ALL_FIELDS)

    def test_values_are_correct(self, sample_df):
        result = get_list_of_candidate_data(sample_df)
        assert result[0]["person_name"] == "Alice Smith"
        assert result[0]["party_id"] == "PP1"


class TestValidateElectionData:
    def test_valid_data_does_not_raise(self, sample_df):
        validate_election_data(sample_df)

    def test_raises_on_inconsistent_party_name(self, sample_df):
        bad_df = pd.concat([
            sample_df,
            pd.DataFrame([make_candidate(person_id="4", party_id="PP1", party_name="Different Name")]),
        ], ignore_index=True)
        with pytest.raises(ValueError, match="party_ids mapped to multiple party_names"):
            validate_election_data(bad_df)

    def test_same_party_id_same_name_does_not_raise(self, sample_df):
        df = pd.concat([sample_df, sample_df], ignore_index=True)
        validate_election_data(df)


class TestGetAndValidateDf:
    def _make_csv(self, rows: list[dict]) -> io.StringIO:
        header = ",".join(ALL_FIELDS)
        lines = [header] + [",".join(str(row.get(f, "")) for f in ALL_FIELDS) for row in rows]
        return io.StringIO("\n".join(lines))

    def test_strips_surrounding_quotes_from_string_fields(self):
        csv = self._make_csv([make_candidate(facebook_page_url='"https://fb.com/alice"', twitter_username='"alice123"')])
        df = get_and_validate_df(csv)
        assert df.iloc[0]["facebook_page_url"] == "https://fb.com/alice"
        assert df.iloc[0]["twitter_username"] == "alice123"

    def test_blank_string_fields_remain_empty(self):
        csv = self._make_csv([make_candidate()])
        df = get_and_validate_df(csv)
        assert df.iloc[0]["facebook_page_url"] == ""



class TestGetCandidateDataByColumn:
    def test_groups_by_election_id(self, sample_df):
        result = get_candidate_data_by_column(sample_df, "election_id")
        assert set(result.keys()) == {"local.2026", "regional.2026"}
        assert len(result["local.2026"]) == 2
        assert len(result["regional.2026"]) == 1

    def test_groups_by_party_name(self, sample_df):
        result = get_candidate_data_by_column(sample_df, "party_name")
        assert set(result.keys()) == {"Party A", "Party B"}
        assert len(result["Party A"]) == 2

    def test_values_are_candidate_dicts(self, sample_df):
        result = get_candidate_data_by_column(sample_df, "election_id")
        for candidate in result["local.2026"]:
            assert set(candidate.keys()) == set(ALL_FIELDS)

