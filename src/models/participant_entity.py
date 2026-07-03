from sqlalchemy import Column, String, Integer, Text, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class EventParticipant(Base):
  """
  event_participantsに対応
  """
  __tablename__ = "event_participants"

  event_id = Column(Integer, ForeignKey("events.event_id", ondelete="CASCADE"), primary_key=True)
  user_id = Column(String(255), ForeignKey("users.user_id", ondelete="CASCADE"), primary_key=True)
  
  preferred_budget = Column(Integer)
  preferred_area_id = Column(Integer, ForeignKey("event_area_candidates.area_candidate_id", ondelete="CASCADE"))
  overall_comment = Column(Text)

  event = relationship("Event", back_populates="participants")
  user = relationship("User", back_populates="participations")
  preferred_area = relationship("EventAreaCandidate", back_populates="preferred_by_participants")
  date_responses = relationship("DateResponse", back_populates="participant", cascade="all, delete-orphan")