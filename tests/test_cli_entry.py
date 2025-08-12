from unittest import mock

import congress_api.cli as cli


def test_cli_success(tmp_path, monkeypatch):
    # Fake command run to avoid network
    class DummyCommand:
        def __init__(self, *args, **kwargs):
            pass
        def run(self):
            p = tmp_path / "outputs" / "x.csv"
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text("congress,sessionNumber,date,memberName,voteCast\n", encoding="utf-8")
            return p

    monkeypatch.setenv("CONGRESS_API_KEY", "k")
    with mock.patch("congress_api.cli.ExportNotVotingCommand", DummyCommand):
        rc = cli.main(["--first", "Ada", "--last", "Lovelace", "--congress", "118"])
        assert rc == 0


def test_cli_error(monkeypatch):
    class FailingCommand:
        def __init__(self, *args, **kwargs):
            pass
        def run(self):
            raise RuntimeError("bad")

    with mock.patch("congress_api.cli.ExportNotVotingCommand", FailingCommand):
        rc = cli.main(["--first", "Ada", "--last", "Lovelace", "--congress", "118"])
        assert rc == 2


