from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv, find_dotenv

from congress_api.services.api_client import CongressApiClient
from congress_api.services.exporter import CsvExporter
from congress_api.services.roll_call_iterator import RollCallIterator
from congress_api.services.votes_filter import VotesFilter
from congress_api.repositories.base import VotesRepository
from congress_api.mappers.roll_call_mapper import RollCallMapper


@dataclass
class ExportNotVotingCommand:
    member_first: str
    member_last: str
    congress_number: int
    outputs_dir: Optional[Path] = None
    repository: Optional[VotesRepository] = None
    api_key: Optional[str] = None

    def run(self) -> Path:
        api_key = self.api_key or self._load_api_key()
        if not api_key:
            raise RuntimeError("CONGRESS_API_KEY is not set in environment or .env file")

        client = CongressApiClient(api_key=api_key)
        iterator = RollCallIterator(client=client, congress_number=self.congress_number)
        filter_service = VotesFilter(target_first=self.member_first, target_last=self.member_last)

        exporter = CsvExporter(outputs_dir=self.outputs_dir)
        exporter.ensure_outputs_dir()
        output_path = exporter.build_output_filepath(self.member_first, self.member_last, self.congress_number)

        # Optionally persist all roll calls if a repository is provided
        if self.repository is not None:
            # Note: iterator is a generator; create a list to allow reuse for filtering
            roll_calls = list(iterator)
            self.repository.save_roll_calls(roll_calls)
            rows = filter_service.iter_member_rows(iter(roll_calls))
        else:
            rows = filter_service.iter_member_rows(iterator)
        exporter.write_rows(output_path, rows)
        return output_path

    @staticmethod
    def _load_api_key() -> Optional[str]:
        # 1) Already in environment
        api_key = os.getenv("CONGRESS_API_KEY")
        if api_key:
            return api_key
        # 2) Load from nearest .env (current working directory preferred)
        dotenv_path = find_dotenv(usecwd=True)
        if dotenv_path:
            load_dotenv(dotenv_path=dotenv_path, override=False)
            api_key = os.getenv("CONGRESS_API_KEY")
            if api_key:
                return api_key
        # 3) Standard load (python-dotenv default search)
        load_dotenv(override=False)
        api_key = os.getenv("CONGRESS_API_KEY")
        if api_key:
            return api_key
        # 4) Manual fallback: read .env in CWD if present
        from pathlib import Path
        env_file = Path.cwd() / ".env"
        if env_file.exists():
            try:
                for line in env_file.read_text(encoding="utf-8").splitlines():
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    if line.startswith("CONGRESS_API_KEY="):
                        _, value = line.split("=", 1)
                        value = value.strip().strip('"').strip("'")
                        if value:
                            os.environ["CONGRESS_API_KEY"] = value
                            return value
            except Exception:
                pass
        return None


@dataclass
class SingleRollCallExportCommand:
    member_first: str
    member_last: str
    congress_number: int
    session_year: int
    roll_call_number: int
    outputs_dir: Optional[Path] = None

    def run(self) -> Path:
        api_key = ExportNotVotingCommand._load_api_key()
        if not api_key:
            raise RuntimeError("CONGRESS_API_KEY is not set in environment or .env file")

        client = CongressApiClient(api_key=api_key)
        resp = client.get_member_votes(self.congress_number, self.session_year, self.roll_call_number)
        if resp.status_code == 404:
            raise RuntimeError("Roll call not found for the given parameters")
        if resp.status_code != 200 or not resp.json:
            raise RuntimeError(f"Unexpected response status: {resp.status_code}")
        if isinstance(resp.json, dict) and resp.json.get("error"):
            raise RuntimeError(str(resp.json.get("error")))

        roll_call = RollCallMapper.from_api_payload(
            congress=self.congress_number,
            roll_call_number=self.roll_call_number,
            payload=resp.json,
        )

        exporter = CsvExporter(outputs_dir=self.outputs_dir)
        exporter.ensure_outputs_dir()
        output_path = exporter.build_output_filepath(self.member_first, self.member_last, self.congress_number)

        vf = VotesFilter(target_first=self.member_first, target_last=self.member_last)
        rows = vf.iter_member_rows(iter([roll_call]))
        exporter.write_rows(output_path, rows)
        return output_path


