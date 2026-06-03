from pydantic import BaseModel, ConfigDict
import array
from models.event_entity import Event
from models.date_candidate_entity import EventDateCandidate
from models.area_candidate_entity import EventAreaCandidate
from models.participant_entity import EventParticipant

class EventDetailResponse(BaseModel):
  #イベント詳細を取得する際に使用
  # Pydanticに「SQLAlchemyのモデル（特殊な型）を扱ってもいいよ」と許可を出す設定
  model_config = ConfigDict(
      arbitrary_types_allowed=True, 
      from_attributes=True
  )

  event: Event
  dateCandidates:list[EventDateCandidate]
  areaCandidates:list[EventAreaCandidate] 
  participantInfo:list[EventParticipant]
