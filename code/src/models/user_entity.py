from sqlalchemy import Column, String
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
  """
  usersテーブルに対応
  """
  __tablename__ = "users"

  user_id = Column(String(255), primary_key=True)
  password_hash = Column(String(255), nullable=False)
  display_name = Column(String(255), nullable=False)

  managed_events = relationship("Event", back_populates="manager")
  participations = relationship("EventParticipant", back_populates="user")