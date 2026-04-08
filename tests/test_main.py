import pandas as pd
import pytest

from main import getfullelectionjson, getlistofcandidates


@pytest.fixture
def sample_df():
    return pd.DataFrame(
        [
            {"person_name": "Alice Smith", "person_id": 1, "party_name": "Party A", "election_id": "local.2026"},
            {"person_name": "Bob Jones", "person_id": 2, "party_name": "Party B", "election_id": "local.2026"},
            {"person_name": "Carol White", "person_id": 3, "party_name": "Party A", "election_id": "regional.2026"},
        ]
    )


class TestGetListOfCandidates:
    def test_returns_list(self, sample_df):
        result = getlistofcandidates(sample_df)
        assert isinstance(result, list)

    def test_each_entry_has_required_keys(self, sample_df):
        result = getlistofcandidates(sample_df)
        for candidate in result:
            assert "person_name" in candidate
            assert "person_id" in candidate
            assert "party_name" in candidate

    def test_each_entry_has_no_extra_keys(self, sample_df):
        result = getlistofcandidates(sample_df)
        for candidate in result:
            assert set(candidate.keys()) == {"person_name", "person_id", "party_name"}

    def test_values_are_correct(self, sample_df):
        result = getlistofcandidates(sample_df)
        assert result[0] == {"person_name": "Alice Smith", "person_id": 1, "party_name": "Party A"}
        assert result[1] == {"person_name": "Bob Jones", "person_id": 2, "party_name": "Party B"}

    def test_length_matches_dataframe(self, sample_df):
        result = getlistofcandidates(sample_df)
        assert len(result) == len(sample_df)

    def test_empty_dataframe_returns_empty_list(self):
        empty_df = pd.DataFrame(columns=["person_name", "person_id", "party_name", "election_id"])
        result = getlistofcandidates(empty_df)
        assert result == []


class TestGetFullElectionJson:
    def test_returns_dict(self, sample_df):
        result = getfullelectionjson(sample_df)
        assert isinstance(result, dict)

    def test_keys_are_election_ids(self, sample_df):
        result = getfullelectionjson(sample_df)
        assert set(result.keys()) == {"local.2026", "regional.2026"}

    def test_candidates_grouped_by_election(self, sample_df):
        result = getfullelectionjson(sample_df)
        assert len(result["local.2026"]) == 2
        assert len(result["regional.2026"]) == 1

    def test_candidate_data_is_correct(self, sample_df):
        result = getfullelectionjson(sample_df)
        assert result["regional.2026"][0] == {
            "person_name": "Carol White",
            "person_id": 3,
            "party_name": "Party A",
        }

    def test_single_election(self):
        df = pd.DataFrame(
            [{"person_name": "X", "person_id": 10, "party_name": "Y", "election_id": "only.2026"}]
        )
        result = getfullelectionjson(df)
        assert list(result.keys()) == ["only.2026"]
        assert len(result["only.2026"]) == 1

    def test_empty_dataframe_returns_empty_dict(self):
        empty_df = pd.DataFrame(columns=["person_name", "person_id", "party_name", "election_id"])
        result = getfullelectionjson(empty_df)
        assert result == {}
