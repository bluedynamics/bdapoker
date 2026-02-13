from __future__ import annotations

from datetime import datetime, timezone
from enum import StrEnum

from pydantic import BaseModel


class Role(StrEnum):
    MODERATOR = "moderator"
    VOTER = "voter"
    SPECTATOR = "spectator"


class Participant(BaseModel):
    id: str
    name: str
    role: Role
    connected: bool = True


class Vote(BaseModel):
    participant_id: str
    value: str


class Round(BaseModel):
    story: str = ""
    story_link: str | None = None
    votes: dict[str, Vote] = {}
    revealed: bool = False
    round_number: int = 1


class Room(BaseModel):
    id: str
    deck_type: str = "fibonacci"
    description_flavor: str = "technical"
    participants: dict[str, Participant] = {}
    current_round: Round | None = None
    history: list[Round] = []
    created_at: datetime = datetime.now(timezone.utc)
    last_activity: datetime = datetime.now(timezone.utc)

    def touch(self) -> None:
        self.last_activity = datetime.now(timezone.utc)

    def public_state(self, deck_cards: list[dict]) -> dict:
        """Serialize room state for broadcast, hiding votes if not revealed."""
        participants = {
            pid: p.model_dump() for pid, p in self.participants.items()
        }
        current_round = None
        if self.current_round:
            cr = self.current_round
            if cr.revealed:
                votes = {
                    pid: v.model_dump() for pid, v in cr.votes.items()
                }
            else:
                votes = {
                    pid: {"participant_id": pid, "has_voted": True}
                    for pid in cr.votes
                }
            current_round = {
                "story": cr.story,
                "story_link": cr.story_link,
                "votes": votes,
                "revealed": cr.revealed,
                "round_number": cr.round_number,
            }
        return {
            "id": self.id,
            "deck_type": self.deck_type,
            "description_flavor": self.description_flavor,
            "participants": participants,
            "current_round": current_round,
            "deck_cards": deck_cards,
        }


class CreateRoomRequest(BaseModel):
    deck_type: str = "fibonacci"
    description_flavor: str = "technical"


class CreateRoomResponse(BaseModel):
    room_id: str
    moderator_token: str
