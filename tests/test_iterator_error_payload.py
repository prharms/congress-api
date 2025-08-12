from congress_api.services.roll_call_iterator import RollCallIterator


class ClientWithErrorPayload:
    def __init__(self):
        self.calls = 0

    def get_member_votes(self, congress_number, session_year, roll_call_number):
        self.calls += 1
        # Return a 200 with an error payload that indicates no more votes
        payload = {
            "error": "No Vote matches the given query.",
            "request": {
                "congress": str(congress_number),
                "format": "json",
                "session": str(session_year),
                "contentType": "application/json",
            },
        }
        return type("Resp", (), {"status_code": 200, "json": payload})


def test_iterator_stops_on_error_payload():
    it = RollCallIterator(client=ClientWithErrorPayload(), congress_number=118)
    records = list(iter(it))
    assert records == []



