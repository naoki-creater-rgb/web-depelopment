from typing import List
from sqlalchemy import func
from sqlalchemy.orm import Session
from models.date_candidate_entity import EventDateCandidate
from models.area_candidate_entity import EventAreaCandidate
from models.date_response_entity import DateResponse
from models.participant_entity import EventParticipant


class EventCandidateRepository:
    def __init__(self, session: Session):
        """Repositoryはセッションをコンストラクタで受け取る"""
        self.session = session

    def bulk_insert_date_candidates(self, event_id: str, date_candidates: List[str]) -> List[EventDateCandidate]:
        """イベント候補日時を一括登録"""
        new_candidates = [
            EventDateCandidate(event_id=event_id, proposed_datetime=dt)
            for dt in date_candidates
        ]
        self.session.add_all(new_candidates)
        self.session.flush()
        for candidate in new_candidates:
            self.session.refresh(candidate)
        return new_candidates

    def bulk_insert_area_candidates(self, event_id: str, area_candidates: List[str]) -> List[EventAreaCandidate]:
        """イベント候補エリアを一括登録"""
        new_candidates = [
            EventAreaCandidate(event_id=event_id, proposed_area=area)
            for area in area_candidates
        ]
        self.session.add_all(new_candidates)
        self.session.flush()
        for candidate in new_candidates:
            self.session.refresh(candidate)
        return new_candidates

    def update_date_candidate_scores(self, event_id: str) -> List[EventDateCandidate]:
        """日程候補のスコアを再計算"""
        score_summary = (
            self.session.query(
                DateResponse.date_candidate_id,
                func.sum(DateResponse.score).label('total')
            )
            .filter(DateResponse.event_id == event_id)
            .group_by(DateResponse.date_candidate_id)
            .all()
        )

        for row in score_summary:
            self.session.query(EventDateCandidate)\
                .filter(EventDateCandidate.date_candidate_id == row.date_candidate_id)\
                .update({"total_score": row.total})

        self.session.flush()
        return self.session.query(EventDateCandidate).filter(EventDateCandidate.event_id == event_id).all()

    def update_area_candidate_scores(self, event_id: str) -> List[EventAreaCandidate]:
        """エリア候補のスコアを再計算"""
        area_summary = (
            self.session.query(
                EventParticipant.preferred_area_id,
                func.count(EventParticipant.user_id).label('total')
            )
            .filter(EventParticipant.event_id == event_id)
            .group_by(EventParticipant.preferred_area_id)
            .all()
        )

        for row in area_summary:
            if row.preferred_area_id is not None:
                self.session.query(EventAreaCandidate)\
                    .filter(EventAreaCandidate.area_candidate_id == row.preferred_area_id)\
                    .update({"total_score": row.total})

        self.session.flush()
        return self.session.query(EventAreaCandidate).filter(EventAreaCandidate.event_id == event_id).all()


