from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterable

from congress_api.domain.models import RollCall


class VotesRepository(ABC):
    @abstractmethod
    def save_roll_calls(self, roll_calls: Iterable[RollCall]) -> None:
        """Persist roll call data."""
        raise NotImplementedError



