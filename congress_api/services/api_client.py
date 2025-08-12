from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any, Optional

import requests


@dataclass
class SimpleResponse:
    status_code: int
    json: Optional[Any]


class CongressApiClient:
    def __init__(self, api_key: str, *, base_url: str = "https://api.congress.gov/v3") -> None:
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")

    def get_member_votes(self, congress: int, session: int, roll_call: int) -> SimpleResponse:
        """Fetch the member votes payload for a given roll call.

        Returns a SimpleResponse with numeric status_code and a json attribute that
        is either a parsed object (dict) or None. Handles transient 429 with a short
        delay and retries, and converts network errors into status_code 0.
        """
        url = (
            f"{self.base_url}/house-vote/{int(congress)}/{int(session)}/{int(roll_call)}/members"
        )
        params = {"api_key": self.api_key, "format": "json"}

        max_attempts = 2
        for attempt in range(max_attempts):
            try:
                resp = requests.get(url, params=params, timeout=30)
            except requests.RequestException:
                return SimpleResponse(status_code=0, json=None)

            # Retry once on 429
            if resp.status_code == 429 and attempt < max_attempts - 1:
                time.sleep(1)
                continue

            parsed = None
            try:
                # Support both mocks where .json is a callable and real responses
                parsed = resp.json() if callable(getattr(resp, "json", None)) else getattr(resp, "json", None)
            except Exception:
                parsed = None

            return SimpleResponse(status_code=resp.status_code, json=parsed)

        # Fallback (should not hit due to return inside loop)
        return SimpleResponse(status_code=0, json=None)


