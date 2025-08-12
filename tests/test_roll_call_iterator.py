from congress_api.services.roll_call_iterator import RollCallIterator


class DummyClient:
    def __init__(self):
        self.calls = []

    def get_member_votes(self, congress_number, session_year, roll_call_number):
        self.calls.append((congress_number, session_year, roll_call_number))
        # Stop after first call per session
        if roll_call_number > 1:
            return type("Resp", (), {"status_code": 404, "json": None})
        payload = {
            "houseRollCallVoteMemberVotes": {
                "sessionNumber": session_year,
                "startDate": "2024-01-01T00:00:00-04:00",
                "results": [],
            }
        }
        return type("Resp", (), {"status_code": 200, "json": payload})


def test_iterator_yields_two_sessions():
    it = RollCallIterator(client=DummyClient(), congress_number=118)
    records = list(iter(it))
    assert len(records) == 2
    assert {r.session_number for r in records} == {1, 2}


