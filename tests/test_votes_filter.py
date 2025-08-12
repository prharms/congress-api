from congress_api.services.votes_filter import VotesFilter
from congress_api.domain.models import RollCall, MemberVote


class DummyIterator:
    def __iter__(self):
        rc = RollCall(
            congress=118,
            session_number=2,
            roll_call_number=1,
            start_date="2024-07-25T10:59:00-04:00",
            members=[
                MemberVote(bioguide_id=None, first_name="Ada", last_name="Lovelace", vote_cast="Not Voting"),
                MemberVote(bioguide_id=None, first_name="Grace", last_name="Hopper", vote_cast="Yea"),
            ],
        )
        yield rc


def test_votes_filter_matches_not_voting():
    vf = VotesFilter(target_first="Ada", target_last="Lovelace")
    rows = list(vf.iter_member_rows(DummyIterator()))
    assert len(rows) == 1
    assert rows[0]["memberName"] == "Ada Lovelace"
    assert rows[0]["voteCast"] == "Not Voting"


