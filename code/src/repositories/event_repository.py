from sqlalchemy.orm import Session, joinedload
from models.event_entity import Event
from models.participant_entity import EventParticipant
from dtos.dtos import EventDetailResponse
import datetime

"""
eventsテーブルを操作するメソッド
"""
class EventRepository:
  @staticmethod
  def createEvent(db: Session, manager_id, event_name, response_deadline, description) -> Event:
    """
    イベントを作成する
    """
    new_event = Event(
        manager_id=manager_id,
        event_name=event_name,
        response_deadline=response_deadline,
        description=description,
        status="unconfirmed"  # 初期ステータス
    )
    
    db.add(new_event)
    db.commit()
    db.refresh(new_event)

    return new_event

  @staticmethod
  def findEventsByManagerId(db: Session, manager_id) -> list[Event]:
    """
    manager_idを持つユーザが幹事をしているイベントを返却
    """
    return db.query(Event).filter(Event.manager_id == manager_id).all()

  @staticmethod
  def updateEventAsConfirmed(db: Session, event_id, confirmed_area_id, confirmed_shop_name, confirmed_budget, confirmed_datetime_id, payment_destination, paypay_link = None) -> Event:
    """
    企画中のイベントの地域、店、予算、日時、送信先を確定する
    """
    event = db.query(Event).filter(Event.event_id == event_id).first()

    if event:
        event.status = 'confirmed'
        event.confirmed_area_id = confirmed_area_id
        event.confirmed_shop_name = confirmed_shop_name
        event.confirmed_budget = confirmed_budget
        event.confirmed_datetime_id = confirmed_datetime_id
        event.payment_destination = payment_destination
        event.paypay_link = paypay_link
        
        db.commit()
        db.refresh(event)
        
    return event

  @staticmethod
  def findEventsByParticipantId(db: Session, user_id) -> list[Event]:
    """
    user_idをもつユーザが参加しているイベントを返却
    """
    return (
        db.query(Event)
        .join(EventParticipant, Event.event_id == EventParticipant.event_id)
        .filter(EventParticipant.user_id == user_id)
        .all()
    )

  @staticmethod
  def findEventDetailById(db:Session, event_id) -> EventDetailResponse:
    """
    イベントの詳細を取得する
    幹事が情報を確定する際に参照
    参加者が回答する際に参照
    """
    event_entity = (
        db.query(Event)
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
    
