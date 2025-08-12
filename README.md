## Congress API

CLI tool to export a specified member's House roll call votes during a given two-year Congress term, using the Congress.gov API. Exports all votes by that member (Yea, Nay, Not Voting, etc.).

### Features
- Export matching votes to CSV in `outputs/`
- Robust, extensible architecture (domain models, mappers, services, commands)
- Ready to scale for future features like SQLite persistence

## Installation
1) Python 3.9+
2) From the project root:

```
pip install -e .
```

## Configuration
Set your API key via environment or `.env` file in the project root:

```
CONGRESS_API_KEY=YOUR_KEY_HERE
```

API documentation: `https://api.congress.gov/`

## Usage
Run the CLI to export all votes for the member in the specified Congress:

```
congress-api --first "FIRST_NAME" --last "LAST_NAME" --congress 118
```

Example:

```
congress-api --first "Jake" --last "Auchincloss" --congress 118
```

This writes a timestamped CSV to `outputs/` with columns:
- `congress`
- `sessionNumber`
- `date`
- `memberName`
- `voteCast`
 - `rollCallNumber`
 - `voteUrl`
 - `voteQuestion`
 - `legislation`

## How it works
- Iterates roll calls for the two session years (1 and 2) for the provided Congress term
- Stops each session when the API returns "No Vote matches the given query" (HTTP 404) or a 200 with that error payload
- Filters all of the member’s votes across all roll calls
- Writes rows to CSV

## Architecture (scalable)
- Domain models: `RollCall`, `MemberVote` (`congress_api/domain/models.py`)
- Mapper: API payload → domain (`congress_api/mappers/roll_call_mapper.py`)
- Services:
  - `CongressApiClient` HTTP client (`congress_api/services/api_client.py`)
  - `RollCallIterator` iterates all roll calls (`congress_api/services/roll_call_iterator.py`)
  - `VotesFilter` filters on domain models (`congress_api/services/votes_filter.py`)
  - `CsvExporter` handles file naming and writing (`congress_api/services/exporter.py`)
- Command: orchestration layer (`congress_api/commands/export_command.py`)
- Repository abstraction (future-ready):
  - `VotesRepository` base (`congress_api/repositories/base.py`)
  - `SqliteVotesRepository` schema + saver (`congress_api/repositories/sqlite_repository.py`)

The CLI currently exports CSVs. Persisting to SQLite can be added by wiring the repository into the CLI; the repository and schema are already implemented for easy integration.

### Example: programmatic usage with SQLite (optional)
```
from pathlib import Path
from congress_api.commands.export_command import ExportNotVotingCommand
from congress_api.repositories.sqlite_repository import SqliteVotesRepository

repo = SqliteVotesRepository(db_path=Path("votes.db"))
cmd = ExportNotVotingCommand(member_first="Ada", member_last="Lovelace", congress_number=118, repository=repo)
csv_path = cmd.run()
print(csv_path)
```

## Testing
All tests live in `tests/` and follow `test_*.py` naming.

```
pytest -q
```

## Project structure
```
congress_api/
  commands/
    export_command.py
  domain/
    models.py
  mappers/
    roll_call_mapper.py
  repositories/
    base.py
    sqlite_repository.py
  services/
    api_client.py
    exporter.py
    roll_call_iterator.py
    votes_filter.py
  __init__.py
tests/
  test_cli_smoke.py
  test_roll_call_iterator.py
  test_votes_filter.py
pyproject.toml
README.md
CLAUDE.md
```

