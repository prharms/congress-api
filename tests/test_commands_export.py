from pathlib import Path
from unittest import mock
import csv

from congress_api.commands.export_command import ExportNotVotingCommand


class DummyRollCallIterator:
    def __init__(self, client=None, congress_number=0):
        self._records = [
            {
                "houseRollCallVoteMemberVotes": {
                    "sessionNumber": 1,
                    "startDate": "2023-02-15T12:00:00-05:00",
                    "voteQuestion": "On Passage",
                    "legislationType": "HRES",
                    "legislationNumber": "43",
                    "results": [
                        {"firstName": "Ryan", "lastName": "Zinke", "voteCast": "Yea"},
                        {"firstName": "Other", "lastName": "Member", "voteCast": "Nay"},
                    ],
                }
            }
        ]

    def __iter__(self):
        from congress_api.mappers.roll_call_mapper import RollCallMapper
        # Yield a single mapped roll call with roll_call_number 1
        yield RollCallMapper.from_api_payload(118, 1, self._records[0])


def test_export_command_full_no_repo(tmp_path, monkeypatch):
    # Ensure API key available
    monkeypatch.setenv("CONGRESS_API_KEY", "k")

    # Route iterator to dummy to avoid network
    with mock.patch("congress_api.commands.export_command.RollCallIterator", DummyRollCallIterator):
        out_dir = tmp_path / "outputs"
        cmd = ExportNotVotingCommand(
            member_first="Ryan",
            member_last="Zinke",
            congress_number=118,
            outputs_dir=out_dir,
        )
        out_path = cmd.run()
        assert out_path.exists()
        rows = list(csv.DictReader(out_path.open("r", encoding="utf-8")))
        assert len(rows) == 1
        assert rows[0]["memberName"] == "Ryan Zinke"


def test_export_command_with_repo(tmp_path, monkeypatch):
    monkeypatch.setenv("CONGRESS_API_KEY", "k")

    class DummyRepo:
        def __init__(self):
            self.saved = []

        def save_roll_calls(self, roll_calls):
            self.saved = list(roll_calls)

    with mock.patch("congress_api.commands.export_command.RollCallIterator", DummyRollCallIterator):
        out_dir = tmp_path / "outputs"
        repo = DummyRepo()
        cmd = ExportNotVotingCommand(
            member_first="Ryan",
            member_last="Zinke",
            congress_number=118,
            outputs_dir=out_dir,
            repository=repo,
        )
        out_path = cmd.run()
        assert out_path.exists()
        assert len(repo.saved) == 1


