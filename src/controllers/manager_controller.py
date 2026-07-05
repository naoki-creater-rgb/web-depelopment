from fastapi import APIRouter
from services.organizer_service import OrganizerService
from controllers.models.manager_models import CreateNewEvent, ConfirmedInformation

router = APIRouter(tags=["organizer"])


@router.get("/manager/events")
def get_manager_events(manager_id: str):
    """ユーザが管理しているイベント一覧を返却する"""
    return OrganizerService.get_managed_events(manager_id)


@router.post("/create/new_event")
def create_new_event(create_new_event: CreateNewEvent):
    """新しくイベントを作成する"""
    return OrganizerService.create_new_event(create_new_event)


@router.post("/confirm_information")
def confirm_information(confirmed_information: ConfirmedInformation):
    """イベント情報を確定する"""
    return OrganizerService.confirm_event(confirmed_information)