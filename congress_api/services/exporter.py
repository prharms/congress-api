"""CSV export utilities.

Responsible for creating the outputs directory, constructing a timestamped
filename, and writing rows to disk in a consistent format.
"""
from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable


OUTPUTS_DIR = Path("outputs")


class CsvExporter:
    """Exporter for writing filtered vote rows to a CSV file."""

    def __init__(self, outputs_dir: Path | None = None) -> None:
        self.outputs_dir = outputs_dir or OUTPUTS_DIR

    def ensure_outputs_dir(self) -> None:
        """Ensure the outputs directory exists."""
        self.outputs_dir.mkdir(parents=True, exist_ok=True)

    def build_output_filepath(
        self, member_first: str, member_last: str, congress_number: int
    ) -> Path:
        """Return a timestamped CSV path under the outputs directory."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = (
            f"{member_first}_{member_last}_congress_{congress_number}_{timestamp}.csv"
        )
        return self.outputs_dir / filename

    def write_rows(self, output_path: Path, rows: Iterable[Dict]) -> None:
        """Write iterable of dict rows using a fixed set/order of columns."""
        fieldnames = [
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
        with output_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for row in rows:
                writer.writerow(row)


