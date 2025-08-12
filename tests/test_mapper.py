from congress_api.mappers.roll_call_mapper import RollCallMapper


def test_roll_call_mapper_builds_members():
    payload = {
        "houseRollCallVoteMemberVotes": {
            "sessionNumber": 2,
            "startDate": "2024-07-25T10:59:00-04:00",
            "result": "Passed",
            "voteQuestion": "On Passage",
            "legislationType": "HRES",
            "legislationNumber": "123",
            "results": [
                {
                    "bioguideID": "A000001",
                    "firstName": "Ada",
                    "lastName": "Lovelace",
                    "voteCast": "Not Voting",
                    "voteParty": "I",
                    "voteState": "UK",
                }
            ],
        }
    }

    rc = RollCallMapper.from_api_payload(congress=118, roll_call_number=1, payload=payload)
    assert rc.congress == 118
    assert rc.session_number == 2
    assert rc.roll_call_number == 1
    assert rc.start_date == "2024-07-25T10:59:00-04:00"
    assert rc.result == "Passed"
    assert rc.vote_question == "On Passage"
    assert rc.legislation_type == "HRES"
    assert rc.legislation_number == "123"
    assert len(rc.members) == 1
    mv = rc.members[0]
    assert mv.bioguide_id == "A000001"
    assert mv.first_name == "Ada"
    assert mv.last_name == "Lovelace"
    assert mv.vote_cast == "Not Voting"
    assert mv.party == "I"
    assert mv.state == "UK"


