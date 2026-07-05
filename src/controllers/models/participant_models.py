from pydantic import BaseModel

class AnswerDateResponse(BaseModel):
  date_candidate_id: int
  score: int
  comment: str

class ParticipantCreateAnswer(BaseModel):
  event_id: int
  user_id: str
  date_responses: list[AnswerDateResponse]
  preferred_budget: int
  preferred_area_id: int
  overall_comment: str