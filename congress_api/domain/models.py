from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class MemberVote:
    bioguide_id: Optional[str]
    first_name: str
    last_name: str
    vote_cast: str
    party: Optional[str] = None
    state: Optional[str] = None

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()


@dataclass
class RollCall:
    congress: int
    session_number: int
    roll_call_number: int
    start_date: Optional[str]
    result: Optional[str] = None
    vote_question: Optional[str] = None
    legislation_type: Optional[str] = None
    legislation_number: Optional[str] = None
    members: List[MemberVote] = field(default_factory=list)


