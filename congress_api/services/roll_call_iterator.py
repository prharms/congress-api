"""Iteration over roll call votes across both session years.

Respects termination signals (HTTP 404 or specific error payload) and prints a
progress message every 10th roll call to balance visibility and performance.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Generator

from .api_client import CongressApiClient
from ..domain.models import RollCall
from ..mappers.roll_call_mapper import RollCallMapper


class RollCallIterator:
    """Iterates all roll call votes across both session years.

    For each of the two session years (1 and 2), starts at roll call 1 and
    increments until terminated by a 404 or a 200 response containing an error
    payload indicating no matching vote.
    """

    def __init__(self, client: CongressApiClient, congress_number: int) -> None:
        self.client = client
        self.congress_number = congress_number

    def __iter__(self) -> Generator[RollCall, None, None]:
        for session_year in (1, 2):
            roll_call = 1
            while True:
                response = self.client.get_member_votes(self.congress_number, session_year, roll_call)
                if response.status_code == 404:
                    break
                if response.status_code != 200 or not response.json:
                    # Skip on transient/non-200 issues
                    roll_call += 1
                    continue
                # Some Congress.gov responses return 200 with an error payload when beyond range
                if isinstance(response.json, dict) and response.json.get("error"):
                    error_msg = str(response.json.get("error", "")).strip()
                    if error_msg.lower().startswith("no vote matches the given query"):
                        break
                if roll_call % 10 == 0:
                    print(
                        f"[INFO] Processing congress={self.congress_number} session={session_year} roll_call={roll_call}"
                    )
                yield RollCallMapper.from_api_payload(
                    congress=self.congress_number,
                    roll_call_number=roll_call,
                    payload=response.json,
                )
                roll_call += 1


