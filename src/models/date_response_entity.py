from sqlalchemy import Column, String, Integer, Text, ForeignKey, ForeignKeyConstraint
from sqlalchemy.orm import relationship
from database import Base

class DateResponse(Base):
    """
    participant_date_responsesに対応
    """
    __tablename__ = "participant_date_responses"

    event_id = Column(Integer, primary_key=True)
    user_id = Column(String(255), primary_key=True)
    date_candidate_id = Column(Integer, ForeignKey("event_date_candidates.date_candidate_id", ondelete="CASCADE"), primary_key=True)

    score = Column(Integer, nullable=False)
    comment = Column(Text)

    __table_args__ = (
        ForeignKeyConstraint(
            ['event_id', 'user_id'],
            ['event_participants.event_id', 'event_participants.user_id'],
            ondelete="CASCADE"
        ),
    )

    participant = relationship("EventParticipant", back_populates="date_responses")
    date_candidate = relationship("EventDateCandidate", back_populates="responses")