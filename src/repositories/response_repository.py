from typing import List, Optional
from sqlalchemy import func
from sqlalchemy.orm import Session
from models.participant_entity import EventParticipant
from models.date_response_entity import DateResponse
from models.area_candidate_entity import EventAreaCandidate
from models.date_candidate_entity import EventDateCandidate


class EventParticipantRepository:
    def __init__(self, session: Session):
        """Repositoryはセッションをコンストラクタで受け取る"""
        self.session = session

    def bulk_insert_participants(self, event_id: str, user_ids: List[str]) -> List[EventParticipant]:
        """イベント参加者を一括登録"""
        new_participants = [
            EventParticipant(event_id=event_id, user_id=user_id)
            for user_id in user_ids
        ]
        self.session.add_all(new_participants)
        self.session.flush()
        for p in new_participants:
            self.session.refresh(p)
        return new_participants

    def find_response_summary_by_event_id(self, event_id: str) -> List[EventParticipant]:
        """イベントの回答サマリーを取得"""
        return self.session.query(EventParticipant).filter(EventParticipant.event_id == event_id).all()

    def update_participant_base_response(
        self,
        event_id: str,
        user_id: str,
        budget: int,
        area_id: int,
        comment: str
    ) -> Optional[EventParticipant]:
        """参加者の基本回答を更新"""
        participant = self.session.query(EventParticipant).filter(
            EventParticipant.event_id == event_id,
            EventParticipant.user_id == user_id
        ).first()

        if participant:
            old_area_id = participant.preferred_area_id
            participant.preferred_budget = budget
            participant.preferred_area_id = area_id
            participant.overall_comment = comment
            self.session.flush()

            affected_areas = {area_id}
            if old_area_id:
                affected_areas.add(old_area_id)

            for aid in affected_areas:
                count = self.session.query(func.count(EventParticipant.user_id)).filter(
                    EventParticipant.preferred_area_id == aid
                ).scalar()
                area_cand = self.session.query(EventAreaCandidate).filter(
                    EventAreaCandidate.area_candidate_id == aid
                ).first()
                if area_cand:
                    area_cand.total_score = count

            self.session.flush()
            self.session.refresh(participant)
        return participant

    def upsert_date_response(
        self,
        event_id: str,
        user_id: str,
        date_candidate_id: str,
        score: int,
        comment: str
    ) -> Optional[DateResponse]:
        """日程回答を登録・更新"""
        existing = self.session.query(DateResponse).filter(
            DateResponse.event_id == event_id,
            DateResponse.user_id == user_id,
            DateResponse.date_candidate_id == date_candidate_id
        ).first()

        if existing:
            existing.score = score
            existing.comment = comment
        else:
            existing = DateResponse(
                event_id=event_id,
                user_id=user_id,
                date_candidate_id=date_candidate_id,
                score=score,
                comment=comment
            )
            self.session.add(existing)

        self.session.flush()

        total = self.session.query(func.sum(DateResponse.score)).filter(
            DateResponse.date_candidate_id == date_candidate_id
        ).scalar() or 0

        date_cand = self.session.query(EventDateCandidate).filter(
            EventDateCandidate.date_candidate_id == date_candidate_id
        ).first()
        if date_cand:
            date_cand.total_score = total

        self.session.flush()
        self.session.refresh(existing)
        return existing