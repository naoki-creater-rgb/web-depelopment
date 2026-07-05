from sqlalchemy import Column, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class EventDateCandidate(Base):
  """
  event_date_candidatesに対応
  """
  __tablename__ = "event_date_candidates"

  date_candidate_id = Column(Integer, primary_key=True, autoincrement=True)
  event_id = Column(Integer, ForeignKey("events.event_id", ondelete="CASCADE"), nullable=False)
  proposed_datetime = Column(DateTime, nullable=False)
  total_score = Column(Integer, default=0)

  event = relationship("Event", foreign_keys=[event_id], back_populates="date_candidates")
  responses = relationship("DateResponse", back_populates="date_candidate", cascade="all, delete-orphan")