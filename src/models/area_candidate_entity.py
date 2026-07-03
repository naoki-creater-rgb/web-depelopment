from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class EventAreaCandidate(Base):
  """
  event_area_candidatesに対応
  """

  __tablename__ = "event_area_candidates"

  area_candidate_id = Column(Integer, primary_key=True, autoincrement=True)
  event_id = Column(Integer, ForeignKey("events.event_id", ondelete="CASCADE"), nullable=False)
  proposed_area = Column(String(255), nullable=False)
  total_score = Column(Integer, default=0)

  event = relationship("Event", back_populates="area_candidates")
  preferred_by_participants = relationship("EventParticipant", back_populates="preferred_area")