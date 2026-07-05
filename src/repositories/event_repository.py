from typing import Optional, List
from sqlalchemy.orm import Session, joinedload
from models.event_entity import Event
from models.participant_entity import EventParticipant
from dtos.dtos import EventDetailResponse
import datetime
import uuid


class EventRepository:
    def __init__(self, session: Session):
        """Repositoryはセッションをコンストラクタで受け取る"""
        self.session = session

    def create_event(self, manager_id: str, event_name: str, response_deadline, description: str) -> Event:
        """イベントを作成"""
        new_event = Event(
            manager_id=manager_id,
            event_name=event_name,
            response_deadline=response_deadline,
            description=description,
            status="planning"
        )
        self.session.add(new_event)
        self.session.flush()
        self.session.refresh(new_event)
        return new_event

    def find_by_manager_id(self, manager_id: str) -> List[Event]:
        """マネージャーIDでイベントを検索"""
        return self.session.query(Event).filter(Event.manager_id == manager_id).all()

    def update_as_confirmed(
        self,
        event_id: str,
        confirmed_area_id: str,
        confirmed_shop_name: str,
        confirmed_budget: float,
        confirmed_datetime_id: str,
        payment_destination: Optional[str] = None,
        paypay_link: Optional[str] = None
    ) -> Optional[Event]:
        """イベントを確定状態に更新"""
        event = self.session.query(Event).filter(Event.event_id == event_id).first()
        if event:
            event.status = 'confirmed'
            event.confirmed_area_id = confirmed_area_id
            event.confirmed_shop_name = confirmed_shop_name
            event.confirmed_budget = confirmed_budget
            event.confirmed_datetime_id = confirmed_datetime_id
            event.payment_destination = payment_destination
            event.paypay_link = paypay_link
            self.session.flush()
        return event

    def find_by_participant_id(self, user_id: str) -> List[Event]:
        """参加者IDでイベントを検索"""
        return (
            self.session.query(Event)
            .options(joinedload(Event.manager))
            .join(EventParticipant, Event.event_id == EventParticipant.event_id)
            .filter(EventParticipant.user_id == user_id)
            .all()
        )

    def find_detail_by_id(self, event_id: str) -> Optional[EventDetailResponse]:
        """イベント詳細を取得"""
        event_entity = (
            self.session.query(Event)
            .options(
                joinedload(Event.date_candidates),
                joinedload(Event.area_candidates),
                joinedload(Event.participants)
            )
            .filter(Event.event_id == event_id)
            .first()
        )

        if not event_entity:
            return None

        response_dto = EventDetailResponse(
            event=event_entity,
            dateCandidates=event_entity.date_candidates,
            areaCandidates=event_entity.area_candidates,
            participantInfo=event_entity.participants
        )
        return response_dto

    def find_by_id(self, event_id: str) -> Optional[Event]:
        """イベントをIDで検索"""
        return self.session.query(Event).filter(Event.event_id == event_id).first()
    
