from unittest import mock
import congress_api.cli as cli


def test_cli_requires_both_or_neither_rollcall_session():
    # rollcall provided without session
    rc = cli.main(["--first", "A", "--last", "B", "--congress", "118", "--rollcall", "5"])
    assert rc == 2
    # session provided without rollcall
    rc = cli.main(["--first", "A", "--last", "B", "--congress", "118", "--session", "1"])
    assert rc == 2


def test_cli_single_rollcall_success(monkeypatch, tmp_path):
    class DummySingle:
        def __init__(self, *args, **kwargs):
            pass

        def run(self):
            p = tmp_path / "outputs" / "x.csv"
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text("congress,sessionNumber,date,memberName,voteCast\n", encoding="utf-8")
            return p

    monkeypatch.setenv("CONGRESS_API_KEY", "k")
    with mock.patch("congress_api.cli.SingleRollCallExportCommand", DummySingle):
        rc = cli.main(["--first", "A", "--last", "B", "--congress", "118", "--session", "1", "--rollcall", "2"])
        assert rc == 0


