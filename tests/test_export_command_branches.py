from pathlib import Path
from unittest import mock
import os
import csv

from congress_api.commands.export_command import (
    ExportNotVotingCommand,
    SingleRollCallExportCommand,
)


def test_export_missing_api_key_raises(monkeypatch, tmp_path):
    # Force API loader to return None
    monkeypatch.setenv("CONGRESS_API_KEY", "", prepend=False)
    with mock.patch(
        "congress_api.commands.export_command.ExportNotVotingCommand._load_api_key",
        return_value=None,
    ):
        cmd = ExportNotVotingCommand(
            member_first="A",
            member_last="B",
            congress_number=118,
            outputs_dir=tmp_path / "outputs",
        )
        try:
            cmd.run()
            assert False, "Expected RuntimeError for missing API key"
        except RuntimeError as e:
            assert "CONGRESS_API_KEY" in str(e)


def test_load_api_key_from_env(monkeypatch):
    monkeypatch.setenv("CONGRESS_API_KEY", "abc123")
    assert ExportNotVotingCommand._load_api_key() == "abc123"


def test_load_api_key_from_dotenv_file(monkeypatch, tmp_path):
    # Ensure no env var present
    if "CONGRESS_API_KEY" in os.environ:
        del os.environ["CONGRESS_API_KEY"]
    # Create .env in CWD
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".env").write_text("CONGRESS_API_KEY=fromfile\n", encoding="utf-8")
    assert ExportNotVotingCommand._load_api_key() == "fromfile"


def test_standard_load_branch(monkeypatch, tmp_path):
    # Ensure no env var present
    if "CONGRESS_API_KEY" in os.environ:
        del os.environ["CONGRESS_API_KEY"]
    # Force find_dotenv to return empty so we hit standard load branch
    with mock.patch("congress_api.commands.export_command.find_dotenv", return_value=""):
        # Patch load_dotenv to set env var
        def fake_load_dotenv(*args, **kwargs):
            os.environ["CONGRESS_API_KEY"] = "from_standard_load"
            return True

        with mock.patch(
            "congress_api.commands.export_command.load_dotenv",
            side_effect=fake_load_dotenv,
        ):
            assert ExportNotVotingCommand._load_api_key() == "from_standard_load"


def test_manual_fallback_branch(monkeypatch, tmp_path):
    # Ensure no env var present
    if "CONGRESS_API_KEY" in os.environ:
        del os.environ["CONGRESS_API_KEY"]
    monkeypatch.chdir(tmp_path)
    # Create .env in CWD; force earlier steps to do nothing
    (tmp_path / ".env").write_text('CONGRESS_API_KEY="quoted_value"\n', encoding="utf-8")
    with mock.patch("congress_api.commands.export_command.find_dotenv", return_value=""):
        with mock.patch("congress_api.commands.export_command.load_dotenv", return_value=False):
            assert ExportNotVotingCommand._load_api_key() == "quoted_value"


def test_manual_fallback_exception(monkeypatch, tmp_path):
    # Ensure no env var present
    if "CONGRESS_API_KEY" in os.environ:
        del os.environ["CONGRESS_API_KEY"]
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".env").write_text("CONGRESS_API_KEY=val\n", encoding="utf-8")
    with mock.patch("congress_api.commands.export_command.find_dotenv", return_value=""):
        with mock.patch("congress_api.commands.export_command.load_dotenv", return_value=False):
            # Force read_text to raise
            with mock.patch("pathlib.Path.read_text", side_effect=Exception("boom")):
                assert ExportNotVotingCommand._load_api_key() is None


def test_single_rollcall_success(monkeypatch, tmp_path):
    monkeypatch.setenv("CONGRESS_API_KEY", "k")

    class DummyClient:
        def __init__(self, api_key: str):
            self.api_key = api_key

        def get_member_votes(self, congress, session, roll_call):
            payload = {
                "houseRollCallVoteMemberVotes": {
                    "sessionNumber": session,
                    "startDate": "2023-02-15T12:00:00-05:00",
                    "voteQuestion": "On Passage",
                    "legislationType": "HRES",
                    "legislationNumber": "43",
                    "results": [
                        {"firstName": "Ryan", "lastName": "Zinke", "voteCast": "Yea"},
                    ],
                }
            }
            return type("Resp", (), {"status_code": 200, "json": payload})

    with mock.patch(
        "congress_api.commands.export_command.CongressApiClient", DummyClient
    ):
        out_dir = tmp_path / "outputs"
        cmd = SingleRollCallExportCommand(
            member_first="Ryan",
            member_last="Zinke",
            congress_number=118,
            session_year=1,
            roll_call_number=43,
            outputs_dir=out_dir,
        )
        out_path = cmd.run()
        assert out_path.exists()
        rows = list(csv.DictReader(out_path.open("r", encoding="utf-8")))
        assert len(rows) == 1
        assert rows[0]["memberName"] == "Ryan Zinke"


def test_single_rollcall_404(monkeypatch):
    monkeypatch.setenv("CONGRESS_API_KEY", "k")

    class DummyClient:
        def __init__(self, api_key: str):
            pass

        def get_member_votes(self, congress, session, roll_call):
            return type("Resp", (), {"status_code": 404, "json": None})

    with mock.patch(
        "congress_api.commands.export_command.CongressApiClient", DummyClient
    ):
        cmd = SingleRollCallExportCommand(
            member_first="Ryan",
            member_last="Zinke",
            congress_number=118,
            session_year=1,
            roll_call_number=99,
        )
        try:
            cmd.run()
            assert False, "Expected RuntimeError for 404"
        except RuntimeError as e:
            assert "not found" in str(e).lower()


def test_single_rollcall_non200(monkeypatch):
    monkeypatch.setenv("CONGRESS_API_KEY", "k")

    class DummyClient:
        def __init__(self, api_key: str):
            pass

    def make_resp(code):
        return type("Resp", (), {"status_code": code, "json": None})

    with mock.patch(
        "congress_api.commands.export_command.CongressApiClient",
        return_value=type("C", (), {"get_member_votes": lambda self, c, s, r: make_resp(500)})(),
    ):
        cmd = SingleRollCallExportCommand(
            member_first="Ryan",
            member_last="Zinke",
            congress_number=118,
            session_year=1,
            roll_call_number=99,
        )
        try:
            cmd.run()
            assert False, "Expected RuntimeError for non-200"
        except RuntimeError as e:
            assert "unexpected" in str(e).lower()


def test_single_rollcall_error_payload(monkeypatch):
    monkeypatch.setenv("CONGRESS_API_KEY", "k")

    class DummyClient:
        def __init__(self, api_key: str):
            pass

        def get_member_votes(self, congress, session, roll_call):
            return type("Resp", (), {"status_code": 200, "json": {"error": "No Vote matches the given query."}})

    with mock.patch(
        "congress_api.commands.export_command.CongressApiClient", DummyClient
    ):
        cmd = SingleRollCallExportCommand(
            member_first="Ryan",
            member_last="Zinke",
            congress_number=118,
            session_year=1,
            roll_call_number=99,
        )
        try:
            cmd.run()
            assert False, "Expected RuntimeError for error payload"
        except RuntimeError as e:
            assert "no vote matches" in str(e).lower()


