from typing import Optional, List
from sqlalchemy.orm import Session
from models.user_entity import User
from models.event_entity import Event
from models.participant_entity import EventParticipant


class UserRepository:
    def __init__(self, session: Session):
        """
        Repositoryはセッションをコンストラクタで受け取る
        UnitOfWorkから渡されたセッションを使用
        """
        self.session = session

    def create_user(self, user_id: str, password: str, display_name: str) -> User:
        """ユーザを登録"""
        new_user = User(
            user_id=user_id,
            password_hash=password,
            display_name=display_name
        )
        self.session.add(new_user)
        self.session.flush()
        self.session.refresh(new_user)
        return new_user

    def find_password_hash_by_id(self, user_id: str) -> Optional[str]:
        """パスワードハッシュを取得"""
        user = self.session.query(User).filter(User.user_id == user_id).first()
        if user:
            return user.password_hash
        return None

    def find_by_id(self, user_id: str) -> Optional[User]:
        """ユーザ情報をIDで検索"""
        return self.session.query(User).filter(User.user_id == user_id).first()

    def find_by_name(self, name: str) -> List[User]:
        """ユーザ名で検索"""
        return self.session.query(User).filter(User.display_name == name).all()

    def find_past_recipients(self, manager_id: str) -> List[User]:
        """過去に参加したユーザを取得"""
        users = self.session.query(User).join(
            EventParticipant, User.user_id == EventParticipant.user_id
        ).join(
            Event, EventParticipant.event_id == Event.event_id
        ).filter(
            Event.manager_id == manager_id
        ).distinct().all()
        return users

    def is_answered_event(self, event_id: str, user_id: str) -> bool:
        """イベントに回答済みかを確認"""
        answered = self.session.query(EventParticipant).filter(
            EventParticipant.event_id == event_id,
            EventParticipant.user_id == user_id
        ).first()
        return answered is not None