from congress_api.services.roll_call_iterator import RollCallIterator
from congress_api.services.votes_filter import VotesFilter
from congress_api.services.exporter import CsvExporter
import csv


class DummyClientMember:
    def get_member_votes(self, congress_number, session_year, roll_call_number):
        # Simulate quick skips until the target roll call
        if session_year != 1:
            return type("Resp", (), {"status_code": 404, "json": None})
        if roll_call_number < 43:
            return type("Resp", (), {"status_code": 500, "json": None})
        if roll_call_number == 43:
            payload = {
                "houseRollCallVoteMemberVotes": {
                    "congress": congress_number,
                    "sessionNumber": 1,
                    "startDate": "2023-02-15T12:00:00-05:00",
                    "voteQuestion": "On Passage",
                    "legislationType": "HRES",
                    "legislationNumber": "43",
                    "results": [
                        {
                            "bioguideID": "Z000017",
                            "firstName": "Ryan",
                            "lastName": "Zinke",
                            "voteCast": "Not Voting",
                            "voteParty": "R",
                            "voteState": "MT",
                        },
                        {
                            "bioguideID": "X000000",
                            "firstName": "Someone",
                            "lastName": "Else",
                            "voteCast": "Yea",
                            "voteParty": "R",
                            "voteState": "TX",
                        },
                    ],
                }
            }
            return type("Resp", (), {"status_code": 200, "json": payload})
        return type("Resp", (), {"status_code": 404, "json": None})


def test_member_row_for_single_rollcall():
    it = RollCallIterator(client=DummyClientMember(), congress_number=118)
    rows = list(VotesFilter(target_first="Ryan", target_last="Zinke").iter_member_rows(it))
    assert len(rows) == 1
    row = rows[0]
    assert row["congress"] == 118
    assert row["sessionNumber"] == 1
    assert row["rollCallNumber"] == 43
    assert row["memberName"] == "Ryan Zinke"
    assert row["voteCast"] == "Not Voting"
    assert row["voteUrl"] == "https://clerk.house.gov/Votes/202343"
    assert row["voteQuestion"] == "On Passage"
    assert row["legislation"] == "HRES 43"


def test_export_csv_standard_format(tmp_path):
    # Arrange: generate the known row via iterator + filter
    it = RollCallIterator(client=DummyClientMember(), congress_number=118)
    rows_gen = VotesFilter(target_first="Ryan", target_last="Zinke").iter_member_rows(it)

    # Act: export to CSV using standard exporter and outputs directory
    outputs_dir = tmp_path / "outputs"
    exporter = CsvExporter(outputs_dir=outputs_dir)
    exporter.ensure_outputs_dir()
    out_path = exporter.build_output_filepath("Ryan", "Zinke", 118)
    exporter.write_rows(out_path, rows_gen)

    # Assert: file exists with standard header and expected row
    assert out_path.exists()
    with out_path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        assert reader.fieldnames == [
            "congress",
            "sessionNumber",
            "date",
            "memberName",
            "voteCast",
            "rollCallNumber",
            "voteUrl",
            "voteQuestion",
            "legislation",
        ]
        rows = list(reader)
        assert len(rows) == 1
        r = rows[0]
        assert r["congress"] == "118"
        assert r["sessionNumber"] == "1"
        assert r["memberName"] == "Ryan Zinke"
        assert r["voteCast"] == "Not Voting"
        assert r["rollCallNumber"] == "43"
        assert r["voteUrl"] == "https://clerk.house.gov/Votes/202343"
        assert r["voteQuestion"] == "On Passage"
        assert r["legislation"] == "HRES 43"



