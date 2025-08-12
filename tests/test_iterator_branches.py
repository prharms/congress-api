from congress_api.services.roll_call_iterator import RollCallIterator


class DummyClientSkip:
    def __init__(self):
        self.calls = 0

    def get_member_votes(self, congress_number, session_year, roll_call_number):
        # First response is non-200, then a valid 200, then 404
        self.calls += 1
        if self.calls == 1:
            return type("Resp", (), {"status_code": 500, "json": None})
        if self.calls == 2:
            payload = {
                "houseRollCallVoteMemberVotes": {
                    "sessionNumber": session_year,
                    "startDate": "2024-01-01T00:00:00-04:00",
                    "results": [],
                }
            }
            return type("Resp", (), {"status_code": 200, "json": payload})
        return type("Resp", (), {"status_code": 404, "json": None})


def test_iterator_skips_non_200():
    it = RollCallIterator(client=DummyClientSkip(), congress_number=118)
    records = list(iter(it))
    assert len(records) >= 1


