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

    def count_answered_participants(self, event_id: str) -> int:
        """イベントに回答済みの参加者数を取得"""
        reply_count = self.session.query(func.count(
            func.distinct(DateResponse.user_id)
        )).filter(DateResponse.event_id == event_id).scalar() or 0
        return reply_count

    def get_date_summaries(self, event_id: str) -> List[dict]:
        """日程候補のサマリーを取得（スコア分布付き）"""
        date_candidates = self.session.query(
            DateResponse.date_candidate_id,
            func.sum(DateResponse.score).label('total_score')
        ).filter(DateResponse.event_id == event_id).group_by(
            DateResponse.date_candidate_id
        ).all()

        summaries = []
        for date_cand_id, total_score in date_candidates:
            # スコア分布を取得（5点、3点、0点の人数）
            score_distribution = self.session.query(
                DateResponse.score,
                func.count(DateResponse.user_id).label('count')
            ).filter(
                DateResponse.event_id == event_id,
                DateResponse.date_candidate_id == date_cand_id
            ).group_by(DateResponse.score).all()

            # スコア分布を辞書に変換
            details = {}
            for score, count in score_distribution:
                details[f"{score}点"] = count

            # 日程候補から日時情報を取得
            date_obj = self.session.query(EventDateCandidate).filter(
                EventDateCandidate.date_candidate_id == date_cand_id
            ).first()

            if date_obj:
                summaries.append({
                    "dateCandidateId": date_cand_id,
                    "datetime": date_obj.proposed_datetime.isoformat() if date_obj.proposed_datetime else None,
                    "totalScore": total_score or 0,
                    "details": details
                })

        return summaries

    def get_area_preferences(self, event_id: str) -> List[dict]:
        """エリア選好のサマリーを取得"""
        area_preferences = self.session.query(
            EventParticipant.preferred_area_id,
            func.count(EventParticipant.user_id).label('count')
        ).filter(
            EventParticipant.event_id == event_id,
            EventParticipant.preferred_area_id.isnot(None)
        ).group_by(EventParticipant.preferred_area_id).all()

        preferences = []
        for area_id, count in area_preferences:
            # エリア情報を取得
            area_obj = self.session.query(EventAreaCandidate).filter(
                EventAreaCandidate.area_candidate_id == area_id
            ).first()

            if area_obj:
                preferences.append({
                    "area_id": area_id,
                    "area": area_obj.proposed_area,
                    "count": count
                })

        return preferences


