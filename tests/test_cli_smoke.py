from pathlib import Path

from congress_api.services.exporter import CsvExporter


def test_exporter_build_and_write(tmp_path):
    outputs_dir = tmp_path / "outputs"
    exporter = CsvExporter(outputs_dir=outputs_dir)
    exporter.ensure_outputs_dir()
    assert outputs_dir.exists()

    p = exporter.build_output_filepath("Ada", "Lovelace", 118)
    assert p.parent == outputs_dir
    assert "Ada_Lovelace_congress_118" in p.name

    rows = [
        {
            "congress": 118,
            "sessionNumber": 2,
            "date": "2024-07-25T10:59:00-04:00",
            "memberName": "Ada Lovelace",
            "voteCast": "Not Voting",
            "rollCallNumber": 325,
            "voteUrl": "clerk.house.gov/Votes/2024325",
        }
    ]
    exporter.write_rows(p, rows)
    assert p.exists()
    content = p.read_text(encoding="utf-8")
    assert "memberName" in content


