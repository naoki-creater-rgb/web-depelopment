from sqlalchemy.orm import Session
from models.participant_entity import EventParticipant
from models.date_response_entity import DateResponse
from sqlalchemy import func
from sqlalchemy.orm import Session
from models.participant_entity import EventParticipant
from models.date_response_entity import DateResponse
from models.area_candidate_entity import EventAreaCandidate
from models.date_candidate_entity import EventDateCandidate

class EventParticipantRepository:
    @staticmethod
    def bulkInsertParticipants(db: Session, event_id: str, user_ids: list[str]) -> list[EventParticipant]:
        """
        選択したユーザーをイベントの参加者（event_participants）として一括登録する
        """
        new_participants = [
            EventParticipant(event_id=event_id, user_id=user_id)
            for user_id in user_ids
        ]
        db.add_all(new_participants)
        db.commit()
        # 各オブジェクトを最新状態（ID確定など）にする
        for p in new_participants:
            db.refresh(p)
        return new_participants

    @staticmethod
    def findResponseSummaryByEventId(db: Session, event_id: str) -> list[EventParticipant]:
        """
        全参加者の希望予算、エリア、全体コメント（event_participantsテーブルの情報）を取得する
        """
        return db.query(EventParticipant).filter(EventParticipant.event_id == event_id).all()

    @staticmethod
    def updateParticipantBaseResponse(db: Session, event_id: int, user_id: str, budget: int, area_id: int, comment: str) -> EventParticipant:
        """
        参加者個人の基本回答を更新し、エリア候補の合計スコアを再計算する
        """
        participant = db.query(EventParticipant).filter(
            EventParticipant.event_id == event_id,
            EventParticipant.user_id == user_id
        ).first()

        if participant:
            old_area_id = participant.preferred_area_id
            participant.preferred_budget = budget
            participant.preferred_area_id = area_id
            participant.overall_comment = comment
            db.commit()

            # エリアのトータルスコアを更新 (選択された回数をカウント)
            # 今回の選択(area_id)と、もし変更前のエリア(old_area_id)があれば両方更新
            affected_areas = {area_id}
            if old_area_id: affected_areas.add(old_area_id)

            for aid in affected_areas:
                count = db.query(func.count(EventParticipant.user_id)).filter(
                    EventParticipant.preferred_area_id == aid
                ).scalar()
                area_cand = db.query(EventAreaCandidate).filter(EventAreaCandidate.area_candidate_id == aid).first()
                if area_cand:
                    area_cand.total_score = count
            
            db.commit()
            db.refresh(participant)
        return participant

    @staticmethod
    def upsertDateResponse(db: Session, event_id: int, user_id: str, date_candidate_id: int, score: int, comment: str) -> DateResponse:
        """
        日程回答を登録・更新し、該当候補日の合計スコアを再計算する
        """
        existing = db.query(DateResponse).filter(
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
            db.add(existing)
        
        db.commit()

        # 日程のトータルスコアを再計算 (その候補日に対する全ユーザーのスコア合計)
        total = db.query(func.sum(DateResponse.score)).filter(
            DateResponse.date_candidate_id == date_candidate_id
        ).scalar() or 0

        date_cand = db.query(EventDateCandidate).filter(
            EventDateCandidate.date_candidate_id == date_candidate_id
        ).first()
        if date_cand:
            date_cand.total_score = total
            db.commit()

        db.refresh(existing)
        return existing

