from sqlalchemy.orm import Session
from models.user_entity import User
from models.event_entity import Event
from models.participant_entity import EventParticipant

import os
from dotenv import load_dotenv

load_dotenv()
db = os.getenv("DATABASE_URL")

"""
usersテーブルを操作するメソッド
"""
class UserRepository:
  @staticmethod
  def createUser(db:Session, id, password, displayName) -> User:
    """
    usersテーブルにユーザを登録する
    """
    new_user = User(
      user_id=id,
      password_hash=password,
      display_name=displayName
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

  @staticmethod
  def findPasswordHashById(db:Session, id) -> str:
    """
    パスワード照会に利用、ハッシュ化されたパスワードを返す
    """
    user = db.query(User).filter(User.user_id == id).first()
    if user:
        return user.password_hash
    return None
  
  @staticmethod
  def findUserById(db :Session, user_id) -> User:
    """
    ユーザ情報を取得する
    もしいない場合はNoneを返す
    """
    return db.query(User).filter(User.user_id == user_id).first()

  @staticmethod
  def findIdByName(db: Session, name) -> list[User]:
    """
    名前から該当するUserインスタンスを返却
    いない場合は[]を返す
    """
    return db.query(User).filter(User.display_name == name).all()

  @staticmethod
  def findPastRecipients(db: Session, manager_id) -> list[User]:
    """
    過去に自分が幹事のイベントに参加したユーザを返す
    もしいない場合は[]を返す
    """
    users = db.query(User).join(
        EventParticipant, User.user_id == EventParticipant.user_id
    ).join(
        Event, EventParticipant.event_id == Event.event_id
    ).filter(
        Event.manager_id == manager_id
    ).distinct().all() # 重複を防ぐために distinct() を追加
    
    return users
