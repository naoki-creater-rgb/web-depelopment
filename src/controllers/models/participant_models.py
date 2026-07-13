from typing import Literal
from pydantic import BaseModel

class AnswerDateResponse(BaseModel):
  date_candidate_id: int
  score: Literal[5, 3, 0]  # 5:参加できる 3:調整すれば参加できる 0:参加できない
  comment: str

class ParticipantCreateAnswer(BaseModel):
  event_id: int
  user_id: str
  date_responses: list[AnswerDateResponse]
  preferred_budget: int
  preferred_area_id: int
  overall_comment: str