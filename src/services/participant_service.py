from pydantic import BaseModel
from models.date_response_entity import DateResponse
from sqlalchemy import exists, and_
from unit_of_work import get_unit_of_work


class ParticipantService:
    class DateResponseInput(BaseModel):
        """日程ごとの回答を定義する型"""
        candidate_id: str
        score: int
        comment: str

    @staticmethod
    def get_participating_events(user_id: str):
        """ユーザが参加しているイベントを取得"""
        try:
            with get_unit_of_work() as uow:
                events = uow.event_repository.find_by_participant_id(user_id)

                unanswered_list = []
                answered_list = []

                for event in events:
                    add_list = {
                        "eventId": event.event_id,
                        "eventName": event.event_name,
                        "deadlineForResponses": event.response_deadline,
                        "managerName": event.manager.display_name
                    }

                    # イベントに対して回答があるかを確認
                    is_answered = uow.session.query(exists().where(
                        and_(
                            DateResponse.event_id == event.event_id,
                            DateResponse.user_id == user_id
                        )
                    )).scalar()

                    if is_answered:
                        answered_list.append(add_list)
                    else:
                        unanswered_list.append(add_list)

                return {
                    "status": "success",
                    "data": {
                        "unanswered": unanswered_list,
                        "answered": answered_list
                    }
                }
        except Exception as e:
            print(f"ERROR in get_participating_events: {e}")
            return {
                "status": "failed",
                "message": "イベント一覧の取得に失敗しました"
            }

    @staticmethod
    def get_event_details(event_id: str):
        """イベント詳細を取得（回答用）"""
        try:
            with get_unit_of_work() as uow:
                event_detail = uow.event_repository.find_detail_by_id(event_id)

                if not event_detail:
                    return {
                        "status": "failed",
                        "message": "イベントが見つかりません"
                    }

                return {
                    "status": "success",
                    "data": event_detail
                }
        except Exception as e:
            print(f"ERROR in get_event_details: {e}")
            return {
                "status": "failed",
                "message": "イベント詳細の取得に失敗しました"
            }

    @staticmethod
    def submit_response(
        event_id: str,
        user_id: str,
        budget: int,
        area_id: int,
        general_comment: str,
        date_responses: list
    ):
        """アンケート結果を送信"""
        try:
            with get_unit_of_work() as uow:
                # 基本回答を更新
                uow.response_repository.update_participant_base_response(
                    event_id,
                    user_id,
                    budget,
                    area_id,
                    general_comment
                )

                # 各日程の回答を登録・更新
                for date_response in date_responses:
                    uow.response_repository.upsert_date_response(
                        event_id,
                        user_id,
                        date_response.candidate_id,
                        date_response.score,
                        date_response.comment
                    )

                return {
                    "status": "success",
                    "message": "回答に成功しました"
                }
        except Exception as e:
            print(f"ERROR in submit_response: {e}")
            return {
                "status": "failed",
                "message": "回答に失敗しました"
            }

    @staticmethod
    def get_confirmed_details(event_id: str):
        """確定済みのイベント情報を取得"""
        try:
            with get_unit_of_work() as uow:
                event = uow.event_repository.find_by_id(event_id)

                if not event:
                    return {
                        "status": "failed",
                        "message": "イベントが見つかりません"
                    }

                return {
                    "status": "success",
                    "data": {
                        "eventId": event.event_id,
                        "eventName": event.event_name,
                        "managerName": event.manager.display_name,
                        "confirmedDetails": {
                            "datetime": event.confirmed_date_candidate.proposed_datetime if event.confirmed_date_candidate else None,
                            "area": event.confirmed_area_id,
                            "shopName": event.confirmed_shop_name,
                            "budget": event.confirmed_budget,
                            "paymentDest": event.payment_destination,
                            "paypayLink": event.paypay_link
                        }
                    }
                }
        except Exception as e:
            print(f"ERROR in get_confirmed_details: {e}")
            return {
                "status": "failed",
                "message": "イベント詳細の取得に失敗しました"
            }