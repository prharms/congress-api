"""Filtering utilities for member vote results.

Contains logic for matching on member name (case-insensitive, tolerant of first
name prefixes) and producing normalized CSV-ready row dictionaries.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Generator

from .roll_call_iterator import RollCallIterator
from ..domain.models import RollCall


@dataclass
class VotesFilter:
    """Filter for locating all rows for a specific member.

    Name matching is case-insensitive. First names are matched with tolerance
    for prefixes (e.g., "Katie" vs "Katherine"), while last names must match
    exactly (ignoring case).
    """

    target_first: str
    target_last: str

    def iter_member_rows(self, iterator: RollCallIterator) -> Generator[Dict, None, None]:
        normalized_first = self.target_first.strip().lower()
        normalized_last = self.target_last.strip().lower()

        for roll_call in iterator:
            for mv in roll_call.members:
                first = mv.first_name.strip().lower()
                last = mv.last_name.strip().lower()
                name_match = (
                    last == normalized_last
                    and (
                        first == normalized_first
                        or first.startswith(normalized_first)
                        or normalized_first.startswith(first)
                    )
                )
                if name_match:
                    year = None
                    if roll_call.start_date and len(roll_call.start_date) >= 4:
                        year = roll_call.start_date[:4]
                    vote_url = None
                    if year:
                        vote_url = f"https://clerk.house.gov/Votes/{year}{roll_call.roll_call_number}"
                    leg_concat = None
                    if roll_call.legislation_type or roll_call.legislation_number:
                        left = (roll_call.legislation_type or "").strip()
                        right = (roll_call.legislation_number or "").strip()
                        leg_concat = (left + (" " if left and right else "") + right) or None

                    yield {
                        "congress": roll_call.congress,
                        "sessionNumber": roll_call.session_number,
                        "date": roll_call.start_date,
                        "memberName": mv.full_name,
                        "voteCast": mv.vote_cast.strip(),
                        "rollCallNumber": roll_call.roll_call_number,
                        "voteUrl": vote_url,
                        "voteQuestion": roll_call.vote_question,
                        "legislation": leg_concat,
                    }


