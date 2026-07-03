from sqlalchemy.orm import Session
from sqlalchemy import func
from models.date_candidate_entity import EventDateCandidate
from models.area_candidate_entity import EventAreaCandidate
from models.date_response_entity import DateResponse
from models.participant_entity import EventParticipant

import os
from dotenv import load_dotenv

load_dotenv()
db = os.getenv("DATABASE_URL")

class EventCandidateRepository:
  @staticmethod
  def bulkInsertDateCandidates(db: Session, event_id, dateCandidates: list[str]) -> list[EventDateCandidate]:
    """
    イベント候補日時をevent_date_candidatesテーブルに追加する
    """
    new_candidates = [
      EventDateCandidate(event_id = event_id, proposed_datetime = dt)
      for dt in dateCandidates
    ]

    db.add_all(new_candidates)
    db.commit()

    #IDが自動採番されるため、refleshを使用
    for candidate in new_candidates:
      db.refresh(candidate)

    return new_candidates
  
  @staticmethod
  def bulkInsertAreaCandidates(db: Session, event_id, areaCandidates: list[str]) -> list[EventAreaCandidate]:
    """
    イベント候補エリアをevent_area_candidatesテーブルに追加する
    """
    new_candidates = [
      EventAreaCandidate(event_id = event_id, proposed_area = area)
      for area in areaCandidates
    ]

    db.add_all(new_candidates)
    db.commit()

    for candidate in new_candidates:
      db.refresh(candidate)

    return new_candidates

  @staticmethod
  def updateDateCandidateScores(db: Session, event_id) -> list[EventDateCandidate]:
    """
    参加者の合計点数を計算し、event_date_candidatesテーブルのtotal_scoreを更新
    """
    score_summary = (
      db.query(
        DateResponse.date_candidate_id,
        func.sum(DateResponse.score).label('total')
        )
        .filter(DateResponse.event_id == event_id)
        .group_by(DateResponse.date_candidate_id)
        .all()
    )

    for row in score_summary:
        db.query(EventDateCandidate)\
          .filter(EventDateCandidate.date_candidate_id == row.date_candidate_id)\
          .update({"total_score": row.total})
    
    db.commit()

    return db.query(EventDateCandidate).filter(EventDateCandidate.event_id == event_id).all()

  @staticmethod
  def updateAreaCandidateScores(db: Session, event_id) -> list[EventAreaCandidate]:
    """
    参加者の合計点数を計算し、event_area_candidatesテーブルのtotal_scoreを更新
    """
    area_summary = (
        db.query(
            EventParticipant.preferred_area_id,
            func.count(EventParticipant.user_id).label('total')
        )
        .filter(EventParticipant.event_id == event_id)
        .group_by(EventParticipant.preferred_area_id)
        .all()
    )

    for row in area_summary:
        if row.preferred_area_id is not None:
            db.query(EventAreaCandidate)\
                .filter(EventAreaCandidate.area_candidate_id == row.preferred_area_id)\
                .update({"total_score": row.total})
    
    db.commit()

    return db.query(EventAreaCandidate).filter(EventAreaCandidate.event_id == event_id).all()


