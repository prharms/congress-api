from __future__ import annotations

from typing import Dict

from congress_api.domain.models import MemberVote, RollCall


class RollCallMapper:
    @staticmethod
    def from_api_payload(congress: int, roll_call_number: int, payload: Dict) -> RollCall:
        block = payload.get("houseRollCallVoteMemberVotes") or {}
        session_number = int(block.get("sessionNumber")) if block.get("sessionNumber") else 0
        start_date = block.get("startDate")
        result = block.get("result")
        vote_question = block.get("voteQuestion")
        legislation_type = block.get("legislationType")
        legislation_number = block.get("legislationNumber")
        members_raw = block.get("results") or []
        members = []
        for mv in members_raw:
            members.append(
                MemberVote(
                    bioguide_id=mv.get("bioguideID"),
                    first_name=str(mv.get("firstName", "")),
                    last_name=str(mv.get("lastName", "")),
                    vote_cast=str(mv.get("voteCast", "")),
                    party=mv.get("voteParty"),
                    state=mv.get("voteState"),
                )
            )
        return RollCall(
            congress=congress,
            session_number=session_number,
            roll_call_number=roll_call_number,
            start_date=start_date,
            result=result,
            vote_question=vote_question,
            legislation_type=legislation_type,
            legislation_number=legislation_number,
            members=members,
        )


