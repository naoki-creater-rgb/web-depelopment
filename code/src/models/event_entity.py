from sqlalchemy import Column, String, Integer, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Event(Base):
  """
  eventsテーブルに対応
  """
  __tablename__ = "events"
  
  #必須の項目
  event_id = Column(Integer, primary_key=True, autoincrement=True)
  manager_id = Column(String(255), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
  event_name = Column(String(255), nullable=False)
  response_deadline = Column(DateTime, nullable=False)
  description = Column(Text)
  status = Column(String(50), default='unconfirmed')

  #必須ではない項目（statusが"confirmed" | "held"であるときに記述）
  confirmed_area_id = Column(String(255))
  confirmed_shop_name = Column(String(255))
  confirmed_budget = Column(String(255))
  confirmed_datetime_id = Column(DateTime)
  payment_destination = Column(String(255))
  paypay_link = Column(String(255))

  manager = relationship("User", back_populates="managed_events")
  participants = relationship("EventParticipant", back_populates="event", cascade="all, delete-orphan")
  date_candidates = relationship("EventDateCandidate", back_populates="event", cascade="all, delete-orphan")
  area_candidates = relationship("EventAreaCandidate", back_populates="event", cascade="all, delete-orphan")