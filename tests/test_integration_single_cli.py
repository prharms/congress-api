import os
import csv
import pytest

from congress_api.commands.export_command import SingleRollCallExportCommand


pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(
        not (os.getenv("RUN_INTEGRATION") == "1" and os.getenv("CONGRESS_API_KEY")),
        reason="Set RUN_INTEGRATION=1 and CONGRESS_API_KEY to run integration tests",
    ),
]


def test_integration_single_rollcall_writes_csv(tmp_path):
    # Use a concrete example; data may vary. This test only asserts file creation and header shape.
    cmd = SingleRollCallExportCommand(
        member_first="Ryan",
        member_last="Zinke",
        congress_number=118,
        session_year=1,
        roll_call_number=43,
        outputs_dir=tmp_path / "outputs",
    )
    out_path = cmd.run()
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


