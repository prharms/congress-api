from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Iterable

from congress_api.domain.models import RollCall, MemberVote
from .base import VotesRepository


SCHEMA_SQL = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS roll_calls (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    congress INTEGER NOT NULL,
    session_number INTEGER NOT NULL,
    roll_call_number INTEGER NOT NULL,
    start_date TEXT,
    result TEXT
);

CREATE TABLE IF NOT EXISTS member_votes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    roll_call_id INTEGER NOT NULL REFERENCES roll_calls(id) ON DELETE CASCADE,
    bioguide_id TEXT,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    vote_cast TEXT NOT NULL,
    party TEXT,
    state TEXT
);
"""


class SqliteVotesRepository(VotesRepository):
    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self._ensure_schema()

    def _get_conn(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def _ensure_schema(self) -> None:
        with self._get_conn() as conn:
            conn.executescript(SCHEMA_SQL)

    def save_roll_calls(self, roll_calls: Iterable[RollCall]) -> None:
        with self._get_conn() as conn:
            cur = conn.cursor()
            for rc in roll_calls:
                cur.execute(
                    """
                    INSERT INTO roll_calls (congress, session_number, roll_call_number, start_date, result)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (rc.congress, rc.session_number, rc.roll_call_number, rc.start_date, rc.result),
                )
                roll_call_id = cur.lastrowid
                for mv in rc.members:
                    cur.execute(
                        """
                        INSERT INTO member_votes (
                            roll_call_id, bioguide_id, first_name, last_name, vote_cast, party, state
                        ) VALUES (?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            roll_call_id,
                            mv.bioguide_id,
                            mv.first_name,
                            mv.last_name,
                            mv.vote_cast,
                            mv.party,
                            mv.state,
                        ),
                    )
            conn.commit()



