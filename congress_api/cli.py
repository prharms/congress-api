"""Command-line interface for the Congress API tool.

Parses user input, validates arguments, and delegates execution to command
objects. Keeps orchestration and business logic separate from the CLI layer.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from typing import List, Optional

from .commands.export_command import (
    ExportNotVotingCommand,
    SingleRollCallExportCommand,
)


@dataclass
class CliArgs:
    """Validated CLI arguments for this program.

    - first: Member first name
    - last: Member last name
    - congress: Two-year Congress number
    - session_year: Optional session year within the Congress (1 or 2)
    - rollcall: Optional roll call number, used only with a session year
    """

    first: str
    last: str
    congress: int
    session_year: Optional[int]
    rollcall: Optional[int]


def parse_args(argv: Optional[List[str]] = None) -> CliArgs:
    """Parse and return validated CLI arguments.

    Also harmonizes whitespace for string inputs.
    """
    parser = argparse.ArgumentParser(
        description=(
            "Export 'Not Voting' roll call votes for a specific House member "
            "in a given two-year Congress term."
        )
    )
    parser.add_argument("--first", required=True, help="Member first name")
    parser.add_argument("--last", required=True, help="Member last name")
    parser.add_argument(
        "--congress", required=True, type=int, help="Congress number (e.g., 118)"
    )
    parser.add_argument(
        "--session",
        type=int,
        choices=[1, 2],
        help="Session year (1 or 2) when using --rollcall",
    )
    parser.add_argument(
        "--rollcall",
        type=int,
        help="Roll call number to fetch a single vote (requires --session)",
    )
    ns = parser.parse_args(argv)
    return CliArgs(
        first=ns.first.strip(),
        last=ns.last.strip(),
        congress=ns.congress,
        session_year=ns.session,
        rollcall=ns.rollcall,
    )


def main(argv: Optional[List[str]] = None) -> int:
    """Program entry point.

    Validates coupled optional arguments and dispatches to either the full
    export command (covers all roll calls) or the single-roll-call command.
    Returns a shell-compatible exit code.
    """
    args = parse_args(argv)
    try:
        # Validate coupled optional args: if one provided, both must be
        if (args.rollcall is None) ^ (args.session_year is None):
            raise ValueError(
                "--rollcall requires --session, and --session requires --rollcall"
            )

        if args.rollcall is not None:
            output_path = SingleRollCallExportCommand(
                member_first=args.first,
                member_last=args.last,
                congress_number=args.congress,
                session_year=args.session_year,
                roll_call_number=args.rollcall,
            ).run()
        else:
            output_path = ExportNotVotingCommand(
                member_first=args.first,
                member_last=args.last,
                congress_number=args.congress,
                api_key=None,
            ).run()
    except Exception as exc:
        print(f"[ERROR] {exc}")
        return 2
    except KeyboardInterrupt:
        print("[INFO] Aborted by user")
        return 130

    print(f"[OK] Wrote results to {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


