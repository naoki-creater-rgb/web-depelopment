from datetime import datetime
from models.event_entity import Status
from unit_of_work import get_unit_of_work


class OrganizerService:
    @staticmethod
    def create_new_event(
        manager_id: str,
        event_name: str,
        response_deadline: str,
        description: str,
        candidate_areas: list,
        candidate_dates: list
    ):
        """新しいイベントを登録"""
        try:
            with get_unit_of_work() as uow:
                # イベントを作成
                new_event = uow.event_repository.create_event(
                    manager_id,
                    event_name,
                    datetime.strptime(response_deadline, "%Y-%m-%d %H:%M"),
                    description
                )
                event_id = new_event.event_id

                # 候補日時を追加
                new_date_candidates = uow.candidate_repository.bulk_insert_date_candidates(
                    event_id,
                    candidate_dates
                )

                # 候補エリアを追加
                new_area_candidates = uow.candidate_repository.bulk_insert_area_candidates(
                    event_id,
                    candidate_areas
                )

                date_candidate_list = [
                    {
                        "id": dc.date_candidate_id,
                        "datetime": dc.proposed_datetime,
                        "totalScore": dc.total_score
                    }
                    for dc in new_date_candidates
                ]

                area_candidate_list = [
                    {
                        "area_id": ac.area_candidate_id,
                        "area": ac.proposed_area
                    }
                    for ac in new_area_candidates
                ]

                return {
                    "status": "success",
                    "data": {
                        "eventId": event_id,
                        "eventName": event_name,
                        "deadlineForResponses": new_event.response_deadline,
                        "managerId": manager_id,
                        "description": description,
                        "status": "planning",
                        "candidateDates": date_candidate_list,
                        "candidateAreas": area_candidate_list
                    }
                }
        except Exception as e:
            print(f"ERROR in create_new_event: {e}")
            return {
                "status": "failed",
                "message": "イベントの登録に失敗しました"
            }

    @staticmethod
    def invite_users(event_id: str, user_ids: list):
        """イベントにユーザを招待"""
        try:
            with get_unit_of_work() as uow:
                uow.response_repository.bulk_insert_participants(event_id, user_ids)
                return {
                    "status": "success",
                    "message": "ユーザを招待しました"
                }
        except Exception:
            return {
                "status": "failed",
                "message": "ユーザ招待に失敗しました"
            }

    @staticmethod
    def get_managed_events(manager_id: str):
        """ユーザが管理しているイベントを取得"""
        try:
            with get_unit_of_work() as uow:
                events = uow.event_repository.find_by_manager_id(manager_id)

                planning = []
                confirmed = []
                completed = []

                for event in events:
                    if event.status == Status.planning:
                        add_list = {
                            "eventId": event.event_id,
                            "eventName": event.event_name,
                            "deadlineForResponses": event.response_deadline
                        }
                        planning.append(add_list)

                    elif event.status == Status.confirmed:
                        datetime_value = None
                        if event.confirmed_date_candidate:
                            datetime_value = event.confirmed_date_candidate.proposed_datetime
                        add_list = {
                            "eventId": event.event_id,
                            "eventName": event.event_name,
                            "datetime": datetime_value
                        }
                        confirmed.append(add_list)

                    elif event.status == Status.completed:
                        datetime_value = None
                        if event.confirmed_date_candidate:
                            datetime_value = event.confirmed_date_candidate.proposed_datetime
                        add_list = {
                            "eventId": event.event_id,
                            "eventName": event.event_name
                        }
                        completed.append(add_list)

                return {
                    "status": "success",
                    "data": {
                        "planning": planning,
                        "confirmed": confirmed,
                        "completed": completed
                    }
                }
        except Exception as e:
            print(f"ERROR in get_managed_events: {e}")
            return {
                "status": "failed",
                "message": "イベント一覧の取得に失敗しました"
            }

    @staticmethod
    def get_event_detail(event_id: str):
        """イベントの詳細を取得（TODO実装待ち）"""
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
            print(f"ERROR in get_event_detail: {e}")
            return {
                "status": "failed",
                "message": "イベント詳細の取得に失敗しました"
            }

    @staticmethod
    def confirm_event(
        event_id: str,
        confirmed_area_id: str,
        confirmed_shop_name: str,
        confirmed_budget: float,
        confirmed_datetime_id: str,
        payment_destination: str,
        paypay_link: str = None
    ):
        """イベント情報を確定"""
        try:
            with get_unit_of_work() as uow:
                event = uow.event_repository.update_as_confirmed(
                    event_id,
                    confirmed_area_id,
                    confirmed_shop_name,
                    confirmed_budget,
                    confirmed_datetime_id,
                    payment_destination,
                    paypay_link
                )

                if not event:
                    return {
                        "status": "failed",
                        "message": "イベントが見つかりません"
                    }

                return {
                    "status": "success",
                    "message": "イベント確定情報登録に成功しました"
                }
        except Exception as e:
            print(f"ERROR in confirm_event: {e}")
            return {
                "status": "failed",
                "message": "イベント確定情報登録に失敗しました"
            }