from typing import Optional, Dict, Any
from unit_of_work import get_unit_of_work


class EventDetailService:
    @staticmethod
    def get_event_detail(event_id: str) -> Dict[str, Any]:
        """イベント詳細情報を取得"""
        try:
            with get_unit_of_work() as uow:
                # イベント基本情報を取得
                event = uow.event_repository.find_by_id(event_id)

                if not event:
                    return {
                        "status": "failed",
                        "message": "イベントが見つかりません"
                    }

                # 参加者情報を取得
                participants = uow.response_repository.find_response_summary_by_event_id(event_id)
                total_participants = len(participants)

                # 回答済み参加者数を取得（Repository経由）
                reply_count = uow.candidate_repository.count_answered_participants(event_id)

                # 日程サマリーを取得（Repository経由）
                date_summaries = uow.candidate_repository.get_date_summaries(event_id)

                # エリア選好を取得（Repository経由）
                area_preferences = uow.candidate_repository.get_area_preferences(event_id)

                # 予算サマリーを取得（Repository経由）
                budget_summary = uow.response_repository.get_budget_summary(event_id)

                # 参加者の詳細回答を取得（Repository経由）
                participant_responses = uow.response_repository.get_participant_responses(event_id)

                # 確定済み情報を取得（データ整形のみ）
                confirmed_details = EventDetailService._format_confirmed_details(event)

                return {
                    "status": "success",
                    "data": {
                        "eventId": event.event_id,
                        "eventName": event.event_name,
                        "deadlineForResponses": event.response_deadline.isoformat() if event.response_deadline else None,
                        "totalParticipants": total_participants,
                        "replyCount": reply_count,
                        "dateSummaries": date_summaries,
                        "areaPreferences": area_preferences,
                        "budgetSummary": budget_summary,
                        "participantResponses": participant_responses,
                        "confirmedDetails": confirmed_details
                    }
                }

        except Exception as e:
            print(f"ERROR in get_event_detail: {e}")
            return {
                "status": "failed",
                "message": "イベント詳細の取得に失敗しました"
            }

    @staticmethod
    def _format_confirmed_details(event) -> Optional[Dict[str, Any]]:
        """確定済み情報をフォーマット"""
        if event.status != "confirmed":
            return None

        return {
            "datetime": event.confirmed_date_candidate.proposed_datetime.isoformat() if event.confirmed_date_candidate else None,
            "area": event.confirmed_area_id,
            "shopName": event.confirmed_shop_name or "",
            "budget": event.confirmed_budget or 0,
            "paymentDest": event.payment_destination or "",
            "paypayLink": event.paypay_link or "",
            "managerComment": event.description or ""
        }
